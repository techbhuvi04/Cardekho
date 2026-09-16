"""Sample Instamart data used ONLY as a fallback when the live scrape returns
zero items (e.g. Swiggy's WAF blocks the current network). This exists so the
matching + comparison UI can be demoed end-to-end even when Instamart cannot
be reached live. Every item returned here is tagged is_sample=True so the
API/UI can label it clearly and it is never confused with real scraped data.
"""

MOCK_CATALOG = {
    "maggi": [
        {"name": "Maggi 2-Minute Masala Noodles", "price": 56.0, "mrp": 60.0, "quantity": "70 g"},
        {"name": "Maggi 2-Minute Noodles", "price": 108.0, "mrp": 120.0, "quantity": "600 g"},
        {"name": "Maggi Masala Noodles Pack of 4", "price": 118.0, "mrp": 120.0, "quantity": "4 x 70 g"},
        {"name": "Maggi Double Masala Instant Noodles", "price": 19.0, "mrp": 20.0, "quantity": "95 g"},
        {"name": "Maggi Hot & Sweet Tomato Chilli Sauce", "price": 82.0, "mrp": 85.0, "quantity": "200 g"},
    ],
    "amul butter": [
        {"name": "Amul Butter Pasteurised", "price": 58.0, "mrp": 61.0, "quantity": "100 g"},
        {"name": "Amul Butter Pasteurised", "price": 109.0, "mrp": 118.0, "quantity": "200 g"},
        {"name": "Amul Salted Butter", "price": 245.0, "mrp": 250.0, "quantity": "500 g"},
    ],
    "amul milk": [
        {"name": "Amul Gold Full Cream Milk", "price": 31.0, "mrp": 33.0, "quantity": "500 ml"},
        {"name": "Amul Taaza Toned Milk", "price": 29.0, "mrp": 30.0, "quantity": "500 ml"},
    ],
    "bread": [
        {"name": "Britannia Bread White", "price": 45.0, "mrp": 50.0, "quantity": "400 g"},
        {"name": "Harvest Gold Brown Bread", "price": 49.0, "mrp": 55.0, "quantity": "400 g"},
    ],
    "eggs": [
        {"name": "Farm Fresh Eggs", "price": 79.0, "mrp": 90.0, "quantity": "6 pcs"},
        {"name": "Farm Fresh Eggs", "price": 149.0, "mrp": 160.0, "quantity": "12 pcs"},
    ],
}


def get_mock_items(query):
    """Return sample items whose catalog key overlaps with the query words."""
    query_lower = query.lower().strip()
    items = MOCK_CATALOG.get(query_lower)
    if items is None:
        query_words = set(query_lower.split())
        for key, catalog_items in MOCK_CATALOG.items():
            if set(key.split()) & query_words:
                items = catalog_items
                break
    if items is None:
        return []
    return [{**item, "image": None, "in_stock": True, "is_sample": True} for item in items]
