# Grocery Price Race

Search a grocery item, pick a delivery location, and see Blinkit vs Instamart
prices side by side — matched product pairs with the cheaper one highlighted.

Built in a ~20 minute time-boxed exercise: `matcher.py` first (with sanity
tests), then scrapers, then the API/UI. Blinkit scrapes live and reliably.
Instamart's WAF blocks automated/datacenter traffic outright (confirmed even
with plain `curl`), so when a live Instamart scrape returns nothing the app
falls back to a small sample dataset just to keep the comparison UI usable —
see `mock_instamart.py` and `DESIGN.md` for details.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Open http://127.0.0.1:8000.

## Notes

- `HEADLESS=0 python app.py` shows the browser — helps with Instamart's bot
  detection on some networks, but a datacenter/cloud IP will still get
  blocked regardless of this flag.
- Locations are edited in the `LOCATIONS` dict in `app.py`.
- Results are cached per (query, location) for 10 minutes; at most 2 scrapes
  run concurrently.
- Desktop sites only, no login, no mobile app.

See `DESIGN.md` for architecture, matching logic and its known failure
cases, and scaling notes.
