"""FastAPI app for Grocery Price Race — Blinkit vs Instamart vs Zepto."""
import asyncio
import time

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from matcher import match_three_way
from mock_instamart import get_mock_items, get_mock_blinkit_items, get_mock_zepto_items
from scrapers import scrape_blinkit, scrape_instamart, scrape_zepto, shutdown_browser

app = FastAPI(title="Grocery Price Race")

LOCATIONS = {
    "nsut_dwarka": {"label": "NSUT Dwarka", "lat": 28.6090, "lon": 77.0350},
    "connaught_place": {"label": "Connaught Place", "lat": 28.6315, "lon": 77.2167},
    "cyber_city_gurugram": {"label": "Cyber City Gurugram", "lat": 28.4950, "lon": 77.0895},
}

CACHE_TTL_S = 10 * 60
_cache = {}  # (query, loc) -> (timestamp, result)

# Cap concurrent scrapes across all requests
_scrape_semaphore = asyncio.Semaphore(3)


async def _bounded_scrape(fn, *args):
    async with _scrape_semaphore:
        return await fn(*args)


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/api/locations")
async def get_locations():
    return [{"key": k, **v} for k, v in LOCATIONS.items()]


@app.delete("/api/cache")
async def clear_cache():
    """Flush all cached search results."""
    count = len(_cache)
    _cache.clear()
    return {"cleared": count, "message": f"Removed {count} cached result(s)"}


@app.get("/api/search")
async def search(q: str = Query(...), loc: str = Query(...)):
    query = q.strip()
    cache_key = (query.lower(), loc)

    now = time.time()
    cached = _cache.get(cache_key)
    if cached and now - cached[0] < CACHE_TTL_S:
        result = dict(cached[1])
        result["cached"] = True
        return result

    location = LOCATIONS.get(loc, LOCATIONS["nsut_dwarka"])
    lat, lon, label = location["lat"], location["lon"], location["label"]

    start = time.time()
    blinkit_result, instamart_result, zepto_result = await asyncio.gather(
        _bounded_scrape(scrape_blinkit, query, lat, lon, label),
        _bounded_scrape(scrape_instamart, query, lat, lon, label),
        _bounded_scrape(scrape_zepto, query, lat, lon, label),
    )
    elapsed = round(time.time() - start, 2)

    # ── Blinkit: use fixture fallback if live returns nothing ────────────
    blinkit_items = blinkit_result["items"]
    blinkit_is_sample = False
    if not blinkit_items and not blinkit_result["error"]:
        blinkit_items = get_mock_blinkit_items(query)
        blinkit_is_sample = bool(blinkit_items)

    # ── Instamart: use fixture fallback if live returns nothing ──────────
    instamart_items = instamart_result["items"]
    instamart_is_sample = False
    if not instamart_items and not instamart_result["error"]:
        instamart_items = get_mock_items(query)
        instamart_is_sample = bool(instamart_items)

    # ── Zepto: use fixture fallback if live returns nothing ──────────────
    zepto_items = zepto_result["items"]
    zepto_is_sample = False
    if not zepto_items and not zepto_result["error"]:
        zepto_items = get_mock_zepto_items(query)
        zepto_is_sample = bool(zepto_items)

    match_output = match_three_way(blinkit_items, instamart_items, zepto_items)

    result = {
        "query": query,
        "location": label,
        "elapsed_s": elapsed,
        "blinkit": {
            "count": len(blinkit_items),
            "error": blinkit_result["error"],
            "is_sample": blinkit_is_sample,
            "elapsed_s": blinkit_result.get("elapsed"),
        },
        "instamart": {
            "count": len(instamart_items),
            "error": instamart_result["error"],
            "is_sample": instamart_is_sample,
            "elapsed_s": instamart_result.get("elapsed"),
        },
        "zepto": {
            "count": len(zepto_items),
            "error": zepto_result["error"],
            "is_sample": zepto_is_sample,
            "elapsed_s": zepto_result.get("elapsed"),
        },
        "matches": match_output["matches"],
        "blinkit_only": match_output["blinkit_only"],
        "instamart_only": match_output["instamart_only"],
        "zepto_only": match_output["zepto_only"],
        "cached": False,
    }

    _cache[cache_key] = (now, result)
    return result


@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_browser()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
