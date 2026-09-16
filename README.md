# Grocery Price Race

Compare grocery prices on **Blinkit** and **Instamart** side by side. Type an
item, pick a delivery location, and get matched product pairs with the
cheaper option highlighted — plus unit prices, savings, and match confidence.

> Built as a ~20 minute time-boxed exercise: matching logic first (with
> sanity tests), then scrapers, then the API and UI.

## What it does

1. You search a query (e.g. "Maggi") and a delivery location.
2. The backend opens a real Chromium browser (via Playwright), seeds it with
   the chosen location, and searches both blinkit.com and
   swiggy.com/instamart concurrently.
3. It captures the JSON the sites' own frontend fetches (not screen-scraped
   HTML), extracting name, price, MRP, pack size, image, and stock status
   for each listing.
4. `matcher.py` pairs up equivalent products across the two sites — same
   brand, same normalized pack size, similar name — and scores each pair's
   confidence.
5. The UI shows matched pairs side by side with the cheaper price in green,
   the saving, unit price (per 100 g / 100 ml / piece), and a confidence %,
   plus separate "only on Blinkit" / "only on Instamart" lists.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Open **http://127.0.0.1:8000**, type a query, pick a location, hit
**Compare prices**. First search for a query/location pair takes ~10-25s
(live scrape); repeat searches within 10 minutes are served from cache
instantly.

Tip: `HEADLESS=0 python app.py` runs with a visible browser window, which
helps on networks where Instamart's bot detection is aggressive (see
[Known limitation](#known-limitation-instamart-blocking) below).

## Project layout

| File | Purpose |
|---|---|
| `app.py` | FastAPI app — serves the UI and the search API, handles caching and concurrency limits |
| `scrapers.py` | Playwright scrapers for Blinkit and Instamart (JSON-network-capture, with a DOM fallback) |
| `matcher.py` | Pairs products across sites, scores confidence, computes unit prices |
| `mock_instamart.py` | Small sample dataset used only when a live Instamart scrape returns nothing (see below) |
| `static/index.html` | Single-page UI, vanilla JS, no build step |
| `DESIGN.md` | Deeper write-up: why browser automation over direct APIs/CSS selectors, where matching heuristics break, how this would scale |

## API

- `GET /api/locations` — the 3 preset delivery locations.
- `GET /api/search?q=<query>&loc=<location key>` — runs the search and
  returns matched pairs, Blinkit-only / Instamart-only items, per-site
  listing counts, and any per-site errors.

Edit preset locations in the `LOCATIONS` dict in `app.py`.

## How matching works (short version)

Product names are tokenized and compared with Jaccard overlap; pack sizes
are normalized (grams, ml, or count — e.g. `4 x 70 g` → `280 g`) and must
match for two listings to be considered the same product. Pairs are then
assigned greedily, highest-confidence first. Full scoring rules and the
specific cases where this heuristic knowingly breaks (salted vs. unsalted,
"Nestle Maggi" vs. "Maggi", combo packs, loose produce) are in `DESIGN.md`.

## Known limitation: Instamart blocking

Blinkit scrapes reliably. Swiggy Instamart runs an aggressive WAF that
blocks automated/datacenter traffic outright — confirmed even with a plain
`curl` request, independent of Playwright or the `HEADLESS` setting. This is
network/IP-based, not a bug in the scraper itself; it may behave
differently on your own machine/network.

When a live Instamart scrape returns zero items (and no explicit error),
the app falls back to a small hardcoded sample dataset in
`mock_instamart.py` just so the side-by-side comparison UI stays usable for
common items (Maggi, Amul butter/milk, bread, eggs). This is a stand-in for
demo purposes, not real-time pricing — see `mock_instamart.py` for the exact
fallback logic.

## Constraints followed

- Desktop sites only — no logins, no mobile app/APK reverse-engineering, no
  deployment.
- At most 2 concurrent scrapes; results cached per (query, location) for 10
  minutes.
- Runs on a fresh machine from this README alone.
