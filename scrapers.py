"""Playwright scrapers for Blinkit and Instamart product search."""
import asyncio
import json
import os
import re
import time
import urllib.parse

from playwright.async_api import async_playwright

HEADLESS = os.environ.get("HEADLESS", "1") != "0"
SITE_TIMEOUT_S = 45
RESULTS_WAIT_S = 12

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_browser = None
_browser_lock = asyncio.Lock()

PRICE_KEYS = ("offer_price", "price", "selling_price", "store_price")
NAME_KEYS = ("product_name", "display_name", "name", "title")
QTY_KEYS = ("unit", "quantity", "weight", "variant")
IMAGE_KEYS = ("image", "image_url", "imageId", "img")
STOCK_KEYS = ("in_stock", "inStock", "available")
MRP_KEYS = ("mrp", "max_retail_price", "listing_price")


async def get_browser():
    global _browser
    async with _browser_lock:
        if _browser is None:
            pw = await async_playwright().start()
            _browser = await pw.chromium.launch(headless=HEADLESS)
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
    image = _first_key(d, IMAGE_KEYS)
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
    start = time.time()
    try:
        browser = await get_browser()
        context = await browser.new_context(
            locale="en-IN",
            user_agent=USER_AGENT,
            geolocation={"latitude": lat, "longitude": lon},
            permissions=["geolocation"],
        )
        location_payload = json.dumps({"address": address, "lat": lat, "lng": lon})
        await context.add_cookies([
            {
                "name": "userLocation",
                "value": urllib.parse.quote(location_payload),
                "domain": ".swiggy.com",
                "path": "/",
            }
        ])
        page = await context.new_page()

        captured = []
        seen = set()

        async def on_response(response):
            url = response.url
            if "/api/instamart" not in url:
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


async def shutdown_browser():
    global _browser
    if _browser is not None:
        await _browser.close()
        _browser = None
