# Design Notes — Grocery Price Race

## 1. Architecture

We drive real Chromium via Playwright and capture the JSON responses the
page's own frontend requests, rather than either calling the sites' APIs
directly or scraping the DOM with CSS selectors.

**Not direct API calls:** Blinkit and Instamart's search APIs require
session tokens minted by their frontend JS (device fingerprints, auth
cookies, signed headers) and are protected by bot-detection layers (WAFs,
challenge pages). Replaying the API from a plain HTTP client either gets
rejected outright or requires reverse-engineering a moving target. Running
a real browser gets us a legitimate session for free.

**Not CSS selectors:** Both sites ship React/Next-style bundles with
hashed, frequently-changing class names (e.g. `_3xK9f`). Selector-based
scraping breaks on every deploy. The JSON payloads underneath, however,
have stable-ish field names (`product_name`, `offer_price`, etc.) because
that's the actual data contract between their frontend and backend — it
changes far less often than presentation markup.

So: launch headless (or headful) Chromium, pre-seed location via cookies +
`localStorage` + Playwright's `geolocation`/`permissions`, navigate to the
search URL, and listen on `page.on("response")` for JSON bodies matching
the site's search/API path. We recursively walk any JSON blob looking for
dict shapes that look like a product (a name-ish key + a price-ish key),
which is deliberately loose — it survives the exact schema shifting
between site updates as long as the *shape* (name + price together)
persists. A DOM-scrape fallback (image + ₹ price in the same card) exists
for when no JSON is captured at all, e.g. if the site changes its
data-fetching approach entirely.

Each site gets an independent 45s timeout and its own try/except boundary
in `scrapers.py`; a failure on one side surfaces as an `error` field and
never prevents the other site's results from being returned.

## 2. Matching — how it works, and where it breaks

`matcher.py` tokenizes each product name (lowercase, strips quantity text
and filler words like "pack"/"combo"/"of"), parses a normalized quantity
(grams, ml, or count — "4 x 70 g" → 280 g), and scores every Blinkit ×
Instamart pair:

1. Different unit dimension (mass vs volume vs count), or same dimension
   but different normalized size → score 0, disqualified outright.
2. Base score = Jaccard overlap of name tokens.
3. Same size on both sides → +0.15. Size missing on either side → −0.15
   (we're less sure, so we discount rather than reward).
4. First token (assumed brand) differs → score × 0.6.

Pairs are then assigned greedily, highest score first, one-to-one, above a
0.5 threshold. Greedy is not globally optimal (a true optimal assignment
would be a min-cost bipartite matching, e.g. the Hungarian algorithm), but
it's simple, fast, and good enough when most true matches have a much
higher score than any false candidate.

**Where this honestly breaks:**

- **Salted vs. unsalted, same size.** "Amul Butter Salted 100 g" and "Amul
  Butter Unsalted 100 g" share every other token and the same size, so
  Jaccard overlap alone pushes them well above threshold — a false match.
  We don't special-case flavor/variant modifiers.
- **Brand-name variants.** "Nestle Maggi Noodles" vs. "Maggi Noodles" — our
  naive "first token is the brand" heuristic picks "nestle" vs "maggi" as
  the brand, mismatches, and penalizes a pair that's actually identical.
- **Combos and multibuys.** "Maggi Noodles 70 g" vs. "Maggi Noodles Buy 2
  Get 1 Free (70 g)" — the multibuy has an effective unit price a third
  lower, but our quantity parser sees the same 70 g and would call these a
  size match, hiding what is actually a bad comparison.
- **Loose produce.** Items like "Tomato (Loose)" often have no fixed pack
  size at all, or are priced per kg with wildly inconsistent naming. These
  frequently fail to match or match spuriously via the "size missing"
  penalty path rather than genuine agreement.
- **Greedy vs. optimal assignment.** With near-duplicate listings (e.g.
  three pack sizes of the same product on both sides), greedy assignment
  can lock in a locally-best pair that blocks a better global pairing
  elsewhere. We accept this trade for simplicity and speed.
- **No barcodes / GTINs available** from either site's public listings, so
  there is no ground-truth identifier to match on — everything here is a
  heuristic over free-text names, which is inherently fuzzy and will never
  reach 100% precision.

## 3. Scaling beyond a demo

- **Cache by dark-store zone, not raw lat/lon.** Blinkit and Instamart both
  serve from a small number of dark stores per city; two nearby lat/lons
  usually map to the same store's catalog and prices. Keying the cache by
  the resolved store/zone ID (once known) instead of raw coordinates
  multiplies the effective cache hit rate for a given number of stored
  entries.
- **Pre-fetch popular queries on a schedule** (e.g. top N searched items
  per zone, refreshed every 10–15 min) so most user requests are cache
  hits instead of live scrapes, keeping p50 latency low without raising
  request volume to the sites.
- **Job queue + warm browser pool.** Replace "spin up a context per
  request" with a queue of scrape jobs consumed by a small pool of
  already-launched, already-logged-in browser contexts, cutting per-job
  startup cost and giving a natural place to enforce concurrency limits.
- **Per-site rate limits**, tuned separately since Blinkit and Instamart
  have different tolerance for automated traffic, with backoff on 403s/
  challenge pages instead of hammering a site that's actively blocking us.
- **Alert on extraction yield drop.** Track "products extracted per
  successful page load" as a metric; a sudden drop to near-zero (as we hit
  with Instamart in this build) means the site changed its response shape
  or bot defenses, and should page someone rather than silently degrade.
- **Persist confirmed matches.** Once a human (or a high-confidence score)
  confirms Product A on Blinkit = Product B on Instamart, store that
  mapping permanently keyed by some stable identifier (site + internal
  product ID) so future searches skip re-matching by name entirely for
  known products.
- **Move toward direct JSON APIs where feasible**, once the mapping of
  stable-ish endpoints and required headers/tokens is well understood from
  browser traffic, using the browser-driven approach as a fallback/audit
  path rather than the sole method — trading some robustness for much
  lower latency and infrastructure cost per search.
