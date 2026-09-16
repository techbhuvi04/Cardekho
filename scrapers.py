"""Playwright scrapers for Blinkit and Instamart product search."""
import asyncio
import json
import os
import re
import time
import urllib.parse
from pathlib import Path

from playwright.async_api import async_playwright

# Path to the cookie file produced by export_swiggy_cookies.py
COOKIE_FILE = Path(__file__).parent / "swiggy_cookies.json"

# Run headless by default (no visible browser window).
# Set HEADLESS=0 env var to show the browser window for debugging.
HEADLESS = os.environ.get("HEADLESS", "1") != "0"
SITE_TIMEOUT_S = 45
RESULTS_WAIT_S = 18   # extra time for Swiggy SPA to hydrate

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_browser = None
_browser_lock = asyncio.Lock()


def _load_swiggy_session():
    """Load cookies + localStorage from the exported Swiggy session file.

    Returns (cookies: list, local_storage: dict) or ([], {}) if file absent.
    """
    if not COOKIE_FILE.exists():
        return [], {}
    try:
        data = json.loads(COOKIE_FILE.read_text())
        return data.get("cookies", []), data.get("local_storage", {})
    except Exception as e:
        print(f"[warn] Could not load {COOKIE_FILE}: {e}")
        return [], {}

# Keys ordered so Swiggy-specific names come first, then Blinkit-specific, then generics
PRICE_KEYS = ("itemPrice", "offerPrice", "offer_price", "price", "selling_price", "store_price", "finalPrice")
NAME_KEYS = ("item_name", "product_name", "display_name", "name", "title")
QTY_KEYS = ("unit", "quantity", "weight", "variant", "itemQuantity")
IMAGE_KEYS = ("cloudinaryImageId", "image", "image_url", "imageId", "img")
STOCK_KEYS = ("in_stock", "inStock", "available", "isAvailable")
MRP_KEYS = ("mrp", "max_retail_price", "listing_price", "slashedPrice")


# Stealth Chromium args — suppress automation flags that sites fingerprint
STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--window-size=1280,800",
    "--start-maximized",
]

# Realistic browser headers to appear as a real Chrome user
BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}


async def get_browser():
    global _browser
    async with _browser_lock:
        if _browser is None:
            pw = await async_playwright().start()
            _browser = await pw.chromium.launch(
                headless=HEADLESS,
                args=STEALTH_ARGS,
            )
    return _browser


def _coerce_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for k in PRICE_KEYS + ("value", "amount"):
            if k in value:
                return _coerce_price(value[k])
        return None
    if isinstance(value, str):
        m = re.search(r"[\d,]+(?:\.\d+)?", value.replace("₹", ""))
        if m:
            return float(m.group(0).replace(",", ""))
    return None


def _first_key(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def _extract_product(d):
    name = _first_key(d, NAME_KEYS)
    price_raw = _first_key(d, PRICE_KEYS)
    if not name or price_raw is None:
        return None
    price = _coerce_price(price_raw)
    if price is None:
        return None
    mrp = _coerce_price(_first_key(d, MRP_KEYS))
    qty = _first_key(d, QTY_KEYS)
    # Swiggy images are Cloudinary IDs, not full URLs — normalise them
    image_raw = _first_key(d, IMAGE_KEYS)
    if image_raw and not str(image_raw).startswith("http"):
        image = f"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_300/{image_raw}"
    else:
        image = image_raw
    stock = _first_key(d, STOCK_KEYS)
    return {
        "name": str(name).strip(),
        "price": price,
        "mrp": mrp if mrp is not None else price,
        "quantity": str(qty).strip() if qty else None,
        "image": image,
        "in_stock": True if stock is None else bool(stock),
    }


def walk_json_for_products(obj, out, seen):
    if isinstance(obj, dict):
        prod = _extract_product(obj)
        if prod:
            key = (prod["name"], prod["price"])
            if key not in seen:
                seen.add(key)
                out.append(prod)
        for v in obj.values():
            walk_json_for_products(v, out, seen)
    elif isinstance(obj, list):
        for item in obj:
            walk_json_for_products(item, out, seen)


def _filter_by_query(items, query):
    query_words = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
    if not query_words:
        return items
    filtered = [
        it for it in items
        if set(re.findall(r"[a-zA-Z0-9]+", it["name"].lower())) & query_words
    ]
    return filtered if filtered else items


async def _dom_fallback(page):
    out = []
    try:
        cards = await page.locator("xpath=//*[.//img][contains(., '₹')]").all()
        for card in cards[:60]:
            try:
                text = await card.inner_text()
            except Exception:
                continue
            if "₹" not in text:
                continue
            m = re.search(r"₹\s*([\d,]+(?:\.\d+)?)", text)
            if not m:
                continue
            price = float(m.group(1).replace(",", ""))
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            name_candidates = [l for l in lines if "₹" not in l and len(l) > 2]
            if not name_candidates:
                continue
            name = max(name_candidates, key=len)
            out.append({
                "name": name,
                "price": price,
                "mrp": price,
                "quantity": None,
                "image": None,
                "in_stock": True,
            })
        # dedupe
        seen = set()
        deduped = []
        for p in out:
            key = (p["name"], p["price"])
            if key not in seen:
                seen.add(key)
                deduped.append(p)
        return deduped
    except Exception:
        return out


async def scrape_blinkit(query, lat, lon, locality="Selected Location"):
    start = time.time()
    try:
        browser = await get_browser()
        context = await browser.new_context(
            locale="en-IN",
            user_agent=USER_AGENT,
            geolocation={"latitude": lat, "longitude": lon},
            permissions=["geolocation"],
        )
        await context.add_cookies([
            {"name": "gr_1_lat", "value": str(lat), "domain": ".blinkit.com", "path": "/"},
            {"name": "gr_1_lon", "value": str(lon), "domain": ".blinkit.com", "path": "/"},
            {"name": "gr_1_locality", "value": locality, "domain": ".blinkit.com", "path": "/"},
        ])
        await context.add_init_script(
            f"""try {{ localStorage.setItem('location', JSON.stringify({{
                lat: {lat}, lon: {lon}, locality: {json.dumps(locality)}
            }})); }} catch (e) {{}}"""
        )
        page = await context.new_page()

        captured = []
        seen = set()

        async def on_response(response):
            url = response.url
            if "/search" not in url:
                return
            try:
                data = await response.json()
            except Exception:
                return
            walk_json_for_products(data, captured, seen)

        page.on("response", on_response)

        url = f"https://blinkit.com/s/?q={urllib.parse.quote(query)}"
        await page.goto(url, timeout=SITE_TIMEOUT_S * 1000, wait_until="domcontentloaded")

        try:
            detect_btn = page.get_by_text(re.compile("detect|use current location", re.I)).first
            if await detect_btn.count() > 0:
                await detect_btn.click(timeout=3000)
                await page.reload(wait_until="domcontentloaded", timeout=SITE_TIMEOUT_S * 1000)
        except Exception:
            pass

        await page.wait_for_timeout(RESULTS_WAIT_S * 1000)

        if not captured:
            captured = await _dom_fallback(page)

        await context.close()
        captured = _filter_by_query(captured, query)
        return {"items": captured, "error": None, "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"items": [], "error": str(e), "elapsed": round(time.time() - start, 2)}


async def scrape_instamart(query, lat, lon, address="Selected Location"):
    """Scrape Swiggy Instamart search results.

    Fixes applied vs original:
    1. Broader API response filter — catches /dapi/, /mapi/, any swiggy search URL.
    2. Richer location cookies (userLocation + tid + SN) so Swiggy skips the
       address-selection wall and loads product results directly.
    3. localStorage pre-seeding for the Swiggy SPA location state.
    4. Smarter location-wall dismissal: tries to type the address into the
       search box if the simple detect-button approach fails.
    5. DOM fallback is guarded — only runs when the page actually has ₹ symbols
       visible (i.e. at least some products rendered).
    """
    start = time.time()
    try:
        browser = await get_browser()
        context = await browser.new_context(
            locale="en-IN",
            user_agent=USER_AGENT,
            geolocation={"latitude": lat, "longitude": lon},
            permissions=["geolocation"],
            extra_http_headers=BROWSER_HEADERS,
            viewport={"width": 1280, "height": 800},
        )
        # Remove the webdriver property so Swiggy's JS fingerprint check passes
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Load real session cookies if available (from export_swiggy_cookies.py)
        session_cookies, session_ls = _load_swiggy_session()
        has_real_session = bool(session_cookies)

        if has_real_session:
            print(f"[instamart] Using real session cookies ({len(session_cookies)} cookies)")
            await context.add_cookies(session_cookies)
        else:
            print("[instamart] No session file found — using synthetic location cookies")

        # Always add location payload (supplements real session or replaces it)
        location_payload = json.dumps({"address": address, "lat": lat, "lng": lon})
        location_cookies = [
            {
                "name": "userLocation",
                "value": urllib.parse.quote(location_payload),
                "domain": ".swiggy.com",
                "path": "/",
            },
            {
                "name": "SN",
                "value": "1",
                "domain": ".swiggy.com",
                "path": "/",
            },
            {
                "name": "locationPopupShown",
                "value": "true",
                "domain": ".swiggy.com",
                "path": "/",
            },
        ]
        # Only add location cookies that aren't already set by the real session
        existing_names = {c["name"] for c in session_cookies}
        extra_cookies = [c for c in location_cookies if c["name"] not in existing_names]
        if extra_cookies:
            await context.add_cookies(extra_cookies)

        # Build localStorage init: merge real session data + synthetic location
        loc_obj = json.dumps({"address": address, "lat": lat, "lng": lon, "annotation": address})
        ls_entries = {
            "userLocation": session_ls.get("userLocation") or loc_obj,
            "selectedLocation": session_ls.get("selectedLocation") or loc_obj,
        }
        # Add any other real session localStorage keys
        for k, v in session_ls.items():
            if k not in ls_entries:
                ls_entries[k] = v

        ls_script = "\n".join(
            f"try {{ localStorage.setItem({json.dumps(k)}, {json.dumps(v)}); }} catch(e) {{}}"
            for k, v in ls_entries.items()
        )
        # Inject localStorage values before every page navigation
        await context.add_init_script(ls_script)

        page = await context.new_page()

        captured = []
        seen = set()

        # FIX 1: Broader URL filter — catch /api/instamart, /dapi/instamart,
        # /mapi/ and any swiggy.com URL that contains 'search' + 'instamart'.
        async def on_response(response):
            url = response.url
            is_swiggy = "swiggy.com" in url
            is_relevant = (
                "/instamart" in url
                or ("search" in url and is_swiggy)
                or "/dapi/" in url
                or "/mapi/" in url
            )
            if not (is_swiggy and is_relevant):
                return
            try:
                data = await response.json()
            except Exception:
                return
            walk_json_for_products(data, captured, seen)

        page.on("response", on_response)

        url = (
            "https://www.swiggy.com/instamart/search"
            f"?custom_back=true&query={urllib.parse.quote(query)}"
        )
        await page.goto(url, timeout=SITE_TIMEOUT_S * 1000, wait_until="domcontentloaded")

        # FIX 3: Multi-strategy location wall dismissal
        try:
            # Strategy A: simple detect / use-current-location button
            detect_btn = page.get_by_text(
                re.compile(r"detect|use current location", re.I)
            ).first
            if await detect_btn.count() > 0:
                await detect_btn.click(timeout=4000)
                await page.wait_for_timeout(2000)

            # Strategy B: if a location search input exists, type the address
            loc_input = page.locator(
                "input[placeholder*='location' i], "
                "input[placeholder*='address' i], "
                "input[placeholder*='area' i]"
            ).first
            if await loc_input.count() > 0:
                await loc_input.fill(address, timeout=3000)
                await page.wait_for_timeout(1500)
                # Click the first suggestion
                suggestion = page.locator(
                    "[data-testid='suggestion'], li[class*='suggestion'], "
                    "div[class*='location-item']"
                ).first
                if await suggestion.count() > 0:
                    await suggestion.click(timeout=3000)
                    await page.wait_for_timeout(1500)

            # Strategy C: dismiss any blocking modal/overlay
            close_btn = page.locator(
                "button[aria-label*='close' i], "
                "button[aria-label*='dismiss' i], "
                "[data-testid='modal-close']"
            ).first
            if await close_btn.count() > 0:
                await close_btn.click(timeout=2000)

        except Exception:
            pass

        await page.wait_for_timeout(RESULTS_WAIT_S * 1000)

        # FIX 4: Only run DOM fallback when some product-like content is visible
        if not captured:
            page_text = await page.inner_text("body")
            if "₹" in page_text:
                captured = await _dom_fallback(page)

        await context.close()
        captured = _filter_by_query(captured, query)
        return {"items": captured, "error": None, "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"items": [], "error": str(e), "elapsed": round(time.time() - start, 2)}


async def scrape_zepto(query, lat, lon, address="Selected Location"):
    """Scrape Zepto search results.

    Uses the same Playwright API-intercept + DOM-fallback strategy as Blinkit.
    Search URL: https://www.zeptonow.com/search?query=<term>
    """
    start = time.time()
    try:
        browser = await get_browser()
        context = await browser.new_context(
            locale="en-IN",
            user_agent=USER_AGENT,
            geolocation={"latitude": lat, "longitude": lon},
            permissions=["geolocation"],
            extra_http_headers=BROWSER_HEADERS,
            viewport={"width": 1280, "height": 800},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Zepto location cookies
        location_payload = json.dumps({"lat": lat, "lng": lon, "address": address})
        await context.add_cookies([
            {"name": "userLocation", "value": urllib.parse.quote(location_payload),
             "domain": ".zeptonow.com", "path": "/"},
            {"name": "location_set", "value": "true",
             "domain": ".zeptonow.com", "path": "/"},
        ])

        # localStorage pre-seeding
        loc_obj = json.dumps({"lat": lat, "lng": lon, "address": address})
        await context.add_init_script(
            f"""try {{ localStorage.setItem('userLocation', {json.dumps(loc_obj)}); }} catch(e) {{}}"""
        )

        page = await context.new_page()

        captured = []
        seen = set()

        async def on_response(response):
            url = response.url
            is_zepto = "zeptonow.com" in url
            is_relevant = (
                "search" in url
                or "/api/" in url
                or "/product" in url
            )
            if not (is_zepto and is_relevant):
                return
            try:
                data = await response.json()
            except Exception:
                return
            walk_json_for_products(data, captured, seen)

        page.on("response", on_response)

        url = f"https://www.zeptonow.com/search?query={urllib.parse.quote(query)}"
        await page.goto(url, timeout=SITE_TIMEOUT_S * 1000, wait_until="domcontentloaded")

        # Try to dismiss location wall if any
        try:
            detect_btn = page.get_by_text(
                re.compile(r"detect|use current location|allow", re.I)
            ).first
            if await detect_btn.count() > 0:
                await detect_btn.click(timeout=4000)
                await page.wait_for_timeout(2000)
        except Exception:
            pass

        await page.wait_for_timeout(RESULTS_WAIT_S * 1000)

        if not captured:
            page_text = await page.inner_text("body")
            if "₹" in page_text:
                captured = await _dom_fallback(page)

        await context.close()
        captured = _filter_by_query(captured, query)
        return {"items": captured, "error": None, "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"items": [], "error": str(e), "elapsed": round(time.time() - start, 2)}


async def shutdown_browser():
    global _browser
    if _browser is not None:
        await _browser.close()
        _browser = None

