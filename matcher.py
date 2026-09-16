"""Matching logic for Grocery Price Race.

Pairs Blinkit and Instamart listings that are (very likely) the same product,
scores confidence, and computes unit prices / savings.
"""
import re
from itertools import product as iterproduct

FILLER_WORDS = {"pack", "combo", "of", "the", "a", "an", "with", "and", "for", "buy"}

# quantity like "70 g", "1 kg", "500ml", "1.5 l", "6 pcs", "4 x 70 g"
_QTY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(g|gm|gram|grams|kg|ml|l|litre|liter|pcs|piece|pieces|pc)\b"
    r"|(\d+(?:\.\d+)?)\s*(g|gm|gram|grams|kg|ml|l|litre|liter|pcs|piece|pieces|pc)\b",
    re.IGNORECASE,
)

_UNIT_TO_GRAMS = {"g": 1, "gm": 1, "gram": 1, "grams": 1, "kg": 1000}
_UNIT_TO_ML = {"ml": 1, "l": 1000, "litre": 1000, "liter": 1000}
_UNIT_TO_COUNT = {"pcs": 1, "piece": 1, "pieces": 1, "pc": 1}


def parse_quantity(text):
    """Return (dimension, normalized_value) where dimension is 'g', 'ml', or 'count'.

    Handles multi-pack sizes like '4 x 70 g' -> ('g', 280).
    Returns (None, None) if no quantity found.
    """
    if not text:
        return None, None
    m = _QTY_RE.search(text)
    if not m:
        return None, None
    if m.group(1) is not None:
        # multipack: count x size unit
        count = float(m.group(1))
        size = float(m.group(2))
        unit = m.group(3).lower()
        total = count * size
    else:
        total = float(m.group(4))
        unit = m.group(5).lower()

    if unit in _UNIT_TO_GRAMS:
        return "g", total * _UNIT_TO_GRAMS[unit]
    if unit in _UNIT_TO_ML:
        return "ml", total * _UNIT_TO_ML[unit]
    if unit in _UNIT_TO_COUNT:
        return "count", total * _UNIT_TO_COUNT[unit]
    return None, None


def _tokenize(name):
    if not name:
        return []
    # strip quantity substring first
    name_no_qty = _QTY_RE.sub(" ", name)
    tokens = re.findall(r"[a-zA-Z0-9]+", name_no_qty.lower())
    return [t for t in tokens if t not in FILLER_WORDS and len(t) > 0]


def _jaccard(tokens_a, tokens_b):
    set_a, set_b = set(tokens_a), set(tokens_b)
    if not set_a or not set_b:
        return 0.0
    inter = set_a & set_b
    union = set_a | set_b
    return len(inter) / len(union)


def score_pair(item_a, item_b):
    """Score a candidate match between two listings (dicts with 'name', 'quantity').

    Returns (score, reason) where score is 0 if disqualified.
    """
    dim_a, val_a = parse_quantity(item_a.get("quantity") or item_a.get("name"))
    dim_b, val_b = parse_quantity(item_b.get("quantity") or item_b.get("name"))

    tokens_a = _tokenize(item_a.get("name"))
    tokens_b = _tokenize(item_b.get("name"))

    # Rule 1: different size or dimension -> no match
    if dim_a and dim_b:
        if dim_a != dim_b:
            return 0.0, "different unit dimension"
        if abs(val_a - val_b) > 0.01 * max(val_a, val_b, 1):
            return 0.0, f"different size ({val_a}{dim_a} vs {val_b}{dim_b})"

    base = _jaccard(tokens_a, tokens_b)
    reason_bits = [f"name overlap {base:.2f}"]

    if dim_a and dim_b and dim_a == dim_b:
        base += 0.15
        reason_bits.append("same size +0.15")
    elif not dim_a or not dim_b:
        base -= 0.15
        reason_bits.append("size missing on one side -0.15")

    brand_a = tokens_a[0] if tokens_a else None
    brand_b = tokens_b[0] if tokens_b else None
    if brand_a and brand_b and brand_a != brand_b:
        base *= 0.6
        reason_bits.append(f"brand mismatch '{brand_a}' vs '{brand_b}' x0.6")

    base = max(0.0, min(1.0, base))
    return base, "; ".join(reason_bits)


def _unit_price(item):
    """Return (unit_label, price_per_unit) e.g. ('100 g', 12.5) or None."""
    price = item.get("price")
    if price is None:
        return None
    dim, val = parse_quantity(item.get("quantity") or item.get("name"))
    if not dim or not val:
        return None
    if dim == "g":
        return "100 g", round(price / val * 100, 2)
    if dim == "ml":
        return "100 ml", round(price / val * 100, 2)
    if dim == "count":
        return "piece", round(price / val, 2)
    return None


def match_listings(blinkit_items, instamart_items, threshold=0.5):
    """Greedily assign one-to-one matches by highest score first.

    Returns dict with keys: matches, blinkit_only, instamart_only.
    """
    candidates = []
    for i, b in enumerate(blinkit_items):
        for j, s in enumerate(instamart_items):
            score, reason = score_pair(b, s)
            if score >= threshold:
                candidates.append((score, reason, i, j))

    candidates.sort(key=lambda c: c[0], reverse=True)

    used_b, used_s = set(), set()
    matches = []
    for score, reason, i, j in candidates:
        if i in used_b or j in used_s:
            continue
        used_b.add(i)
        used_s.add(j)
        b, s = blinkit_items[i], instamart_items[j]
        bp, sp = b.get("price"), s.get("price")
        cheaper, saving = None, 0
        if bp is not None and sp is not None:
            if bp < sp:
                cheaper, saving = "blinkit", round(sp - bp, 2)
            elif sp < bp:
                cheaper, saving = "instamart", round(bp - sp, 2)
            else:
                cheaper, saving = "tie", 0
        matches.append({
            "blinkit": b,
            "instamart": s,
            "blinkit_unit_price": _unit_price(b),
            "instamart_unit_price": _unit_price(s),
            "confidence": round(score, 2),
            "reason": reason,
            "cheaper": cheaper,
            "saving": saving,
        })

    blinkit_only = [b for i, b in enumerate(blinkit_items) if i not in used_b]
    instamart_only = [s for j, s in enumerate(instamart_items) if j not in used_s]

    return {
        "matches": matches,
        "blinkit_only": blinkit_only,
        "instamart_only": instamart_only,
    }


def _greedy_pairs(items_a, items_b, threshold=0.5):
    """Return list of (i, j, score) greedy one-to-one pairs."""
    cands = []
    for i, a in enumerate(items_a):
        for j, b in enumerate(items_b):
            sc, _ = score_pair(a, b)
            if sc >= threshold:
                cands.append((sc, i, j))
    cands.sort(key=lambda c: c[0], reverse=True)
    used_a, used_b = set(), set()
    pairs = []
    for sc, i, j in cands:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        pairs.append((i, j, sc))
    return pairs, used_a, used_b


def match_three_way(blinkit_items, instamart_items, zepto_items, threshold=0.5):
    """Three-way matching: Blinkit × Instamart × Zepto.

    Strategy:
    1. Match Blinkit ↔ Instamart (greedy).
    2. For each matched pair, try to find a matching Zepto item.
    3. Remaining Zepto items are matched against unmatched Blinkit / Instamart.
    4. Compute cheapest across all available platforms per row.

    Returns dict with keys:
        matches: list of {blinkit, instamart, zepto, cheapest, saving, confidence}
        blinkit_only, instamart_only, zepto_only: unmatched items.
    """
    # Step 1: Blinkit ↔ Instamart pairs
    bi_pairs, used_b, used_i = _greedy_pairs(blinkit_items, instamart_items, threshold)

    # Step 2: for each B↔I pair, try to attach a Zepto match
    used_z = set()
    rows = []
    for bi, ii, bi_score in bi_pairs:
        b_item = blinkit_items[bi]
        best_z, best_zj, best_zscore = None, -1, 0
        for zj, z_item in enumerate(zepto_items):
            if zj in used_z:
                continue
            sc, _ = score_pair(b_item, z_item)
            if sc >= threshold and sc > best_zscore:
                best_z, best_zj, best_zscore = z_item, zj, sc
        if best_zj >= 0:
            used_z.add(best_zj)
        rows.append((bi, ii, best_zj, max(bi_score, best_zscore) if best_z else bi_score))

    # Step 3: remaining Zepto ↔ remaining Blinkit
    leftover_b = [i for i in range(len(blinkit_items)) if i not in used_b]
    leftover_i = [j for j in range(len(instamart_items)) if j not in used_i]
    leftover_z = [k for k in range(len(zepto_items)) if k not in used_z]

    for zk in list(leftover_z):
        z_item = zepto_items[zk]
        best_idx, best_src, best_sc = -1, None, 0
        for bi in leftover_b:
            sc, _ = score_pair(blinkit_items[bi], z_item)
            if sc >= threshold and sc > best_sc:
                best_idx, best_src, best_sc = bi, "blinkit", sc
        for ii in leftover_i:
            sc, _ = score_pair(instamart_items[ii], z_item)
            if sc >= threshold and sc > best_sc:
                best_idx, best_src, best_sc = ii, "instamart", sc
        if best_idx >= 0:
            leftover_z.remove(zk)
            used_z.add(zk)
            if best_src == "blinkit":
                rows.append((best_idx, -1, zk, best_sc))
                used_b.add(best_idx)
                leftover_b.remove(best_idx)
            else:
                rows.append((-1, best_idx, zk, best_sc))
                used_i.add(best_idx)
                leftover_i.remove(best_idx)

    # Build final match list
    matches = []
    for bi, ii, zk, score in rows:
        b_item = blinkit_items[bi] if bi >= 0 else None
        i_item = instamart_items[ii] if ii >= 0 else None
        z_item = zepto_items[zk] if zk is not None and zk >= 0 else None

        prices = {}
        if b_item and b_item.get("price") is not None:
            prices["blinkit"] = b_item["price"]
        if i_item and i_item.get("price") is not None:
            prices["instamart"] = i_item["price"]
        if z_item and z_item.get("price") is not None:
            prices["zepto"] = z_item["price"]

        if prices:
            min_plat = min(prices, key=prices.get)
            max_price = max(prices.values())
            min_price = prices[min_plat]
            saving = round(max_price - min_price, 2)
            if all(p == min_price for p in prices.values()):
                cheapest = "tie"
                saving = 0
            else:
                cheapest = min_plat
        else:
            cheapest, saving = None, 0

        matches.append({
            "blinkit": b_item,
            "instamart": i_item,
            "zepto": z_item,
            "blinkit_unit_price": _unit_price(b_item) if b_item else None,
            "instamart_unit_price": _unit_price(i_item) if i_item else None,
            "zepto_unit_price": _unit_price(z_item) if z_item else None,
            "confidence": round(score, 2),
            "cheapest": cheapest,
            "saving": saving,
        })

    blinkit_only = [blinkit_items[i] for i in range(len(blinkit_items)) if i not in used_b]
    instamart_only = [instamart_items[j] for j in range(len(instamart_items)) if j not in used_i]
    zepto_only = [zepto_items[k] for k in range(len(zepto_items)) if k not in used_z]

    return {
        "matches": matches,
        "blinkit_only": blinkit_only,
        "instamart_only": instamart_only,
        "zepto_only": zepto_only,
    }


if __name__ == "__main__":
    # quick sanity tests
    a = {"name": "Maggi 2-Minute Noodles", "quantity": "70 g", "price": 14}
    b = {"name": "Maggi 2-Minute Masala Noodles", "quantity": "70 g", "price": 15}
    c = {"name": "Maggi 2-Minute Noodles Pack of 4", "quantity": "4 x 70 g", "price": 56}

    s1, r1 = score_pair(a, b)
    print("Maggi 70g vs Maggi 70g:", s1, r1)
    assert s1 >= 0.5, "same-size Maggi should match"

    s2, r2 = score_pair(a, c)
    print("Maggi 70g vs Maggi 4x70g:", s2, r2)
    assert s2 == 0.0, "different size (280g vs 70g) must not match"

    result = match_listings([a, c], [b])
    assert len(result["matches"]) == 1
    assert result["matches"][0]["instamart"] is b
    print("match_listings ok:", result)

    # 3-way test
    z = {"name": "Maggi Masala Noodles", "quantity": "70 g", "price": 12}
    r3 = match_three_way([a], [b], [z])
    assert len(r3["matches"]) == 1
    assert r3["matches"][0]["cheapest"] == "zepto"
    print("match_three_way ok:", r3["matches"][0]["cheapest"], r3["matches"][0]["saving"])

    print("All matcher sanity tests passed.")

