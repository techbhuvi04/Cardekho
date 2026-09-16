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
    print("All matcher sanity tests passed.")
