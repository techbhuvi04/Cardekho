"""Paired Blinkit + Instamart catalog fixtures.

Ported from src/server/fixtures/sampleData.ts — 18+ categories, 100+ authentic
SKUs with realistic price variations. Used ONLY as a fallback when the live
Playwright scraper returns zero items.

Every item is tagged is_sample=True so the UI can clearly label it.
"""

# ---------------------------------------------------------------------------
# PAIRED CATALOG  (key = search keyword)
# Each entry: { 'blinkit': [...], 'instamart': [...] }
# ---------------------------------------------------------------------------
PAIRED_CATALOG: dict = {
    # ── 1. BUTTER & CHEESE ──────────────────────────────────────────────────
    "butter": {
        "blinkit": [
            {"name": "Amul Pasteurised Butter",        "brand": "Amul",         "quantity": "500 g",  "price": 275, "mrp": 275, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/160a.jpg",  "in_stock": True},
            {"name": "Amul Pasteurised Butter",        "brand": "Amul",         "quantity": "100 g",  "price": 56,  "mrp": 58,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/159a.jpg",  "in_stock": True},
            {"name": "Amul Garlic & Herbs Butter",     "brand": "Amul",         "quantity": "100 g",  "price": 60,  "mrp": 60,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/2349a.jpg", "in_stock": True},
            {"name": "Mother Dairy Pasteurised Butter","brand": "Mother Dairy", "quantity": "500 g",  "price": 270, "mrp": 275, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/4890a.jpg", "in_stock": False},
        ],
        "instamart": [
            {"name": "Amul Butter - Pasteurised",      "brand": "Amul",         "quantity": "500g",   "price": 270, "mrp": 275, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_butter_500g.png",    "in_stock": True},
            {"name": "Amul Butter",                    "brand": "Amul",         "quantity": "100 g",  "price": 58,  "mrp": 58,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_butter_100g.png",    "in_stock": True},
            {"name": "Amul Garlic and Herbs Butter",   "brand": "Amul",         "quantity": "100g",   "price": 59,  "mrp": 60,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_garlic_butter.png",  "in_stock": True},
            {"name": "President Salted Butter Tub",    "brand": "President",    "quantity": "200 g",  "price": 160, "mrp": 170, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/president_butter.png",    "in_stock": True},
        ],
    },

    # ── 2. NOODLES & MAGGI ──────────────────────────────────────────────────
    "maggi": {
        "blinkit": [
            {"name": "Maggi 2-Minute Masala Instant Noodles", "brand": "Maggi", "quantity": "280 g (Pack of 4 x 70g)", "price": 56,  "mrp": 60,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/1054a.jpg", "in_stock": True},
            {"name": "Maggi 2-Minute Masala Instant Noodles", "brand": "Maggi", "quantity": "560 g (Pack of 8)",       "price": 110, "mrp": 120, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/1055a.jpg", "in_stock": True},
            {"name": "Maggi Special Masala Instant Noodles",  "brand": "Maggi", "quantity": "70 g",                   "price": 20,  "mrp": 20,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/3452a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Maggi 2 Minute Masala Noodles - 4 Pack",       "brand": "Maggi", "quantity": "280g",   "price": 58,  "mrp": 60,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/maggi_4pack.png",  "in_stock": True},
            {"name": "Maggi 2-Minute Masala Noodles Pack of 8",       "brand": "Maggi", "quantity": "560 g",  "price": 108, "mrp": 120, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/maggi_8pack.png",  "in_stock": True},
            {"name": "Maggi Nutri-licious Oats Masala Noodles",       "brand": "Maggi", "quantity": "73 g",   "price": 25,  "mrp": 25,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/maggi_oats.png",   "in_stock": True},
        ],
    },

    # ── 3. MILK ─────────────────────────────────────────────────────────────
    "milk": {
        "blinkit": [
            {"name": "Amul Taaza Homogenised Toned Milk",           "brand": "Amul",       "quantity": "1 L",    "price": 74, "mrp": 75, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/19512a.jpg", "in_stock": True},
            {"name": "Amul Gold Homogenised Standardised Milk",     "brand": "Amul",       "quantity": "1 L",    "price": 82, "mrp": 85, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/19513a.jpg", "in_stock": True},
            {"name": "Nandini Toned Fresh Milk",                    "brand": "Nandini",    "quantity": "500 ml", "price": 24, "mrp": 24, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/1023a.jpg",  "in_stock": True},
        ],
        "instamart": [
            {"name": "Amul Taaza Toned Milk (Tetra Pak)",           "brand": "Amul",       "quantity": "1L",     "price": 75, "mrp": 75, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_taaza_1l.png",    "in_stock": True},
            {"name": "Amul Gold Full Cream Milk (Tetra Pak)",       "brand": "Amul",       "quantity": "1 L",    "price": 84, "mrp": 85, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_gold_1l.png",     "in_stock": True},
            {"name": "Nandini Toned Milk Pouch",                    "brand": "Nandini",    "quantity": "500ml",  "price": 24, "mrp": 24, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/nandini_milk.png",      "in_stock": True},
        ],
    },

    # ── 4. ATTA / FLOUR ─────────────────────────────────────────────────────
    "atta": {
        "blinkit": [
            {"name": "Aashirvaad Superior MP Whole Wheat Chakki Atta", "brand": "Aashirvaad", "quantity": "5 kg", "price": 245, "mrp": 275, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/16084a.jpg", "in_stock": True},
            {"name": "Fortune Chakki Fresh Whole Wheat Atta",          "brand": "Fortune",    "quantity": "5 kg", "price": 220, "mrp": 250, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/18021a.jpg", "in_stock": True},
            {"name": "Aashirvaad Select 100% Sharbati Wheat Atta",     "brand": "Aashirvaad", "quantity": "5 kg", "price": 310, "mrp": 340, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/16085a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Aashirvaad Shudh Chakki Whole Wheat Atta",       "brand": "Aashirvaad", "quantity": "5kg",  "price": 249, "mrp": 275, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/aashirvaad_atta_5kg.png", "in_stock": True},
            {"name": "Fortune Chakki Fresh Atta",                       "brand": "Fortune",    "quantity": "5 kg", "price": 215, "mrp": 250, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/fortune_atta_5kg.png",     "in_stock": True},
            {"name": "Aashirvaad Select Sharbati Atta",                 "brand": "Aashirvaad", "quantity": "5kg",  "price": 315, "mrp": 340, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/aashirvaad_select.png",    "in_stock": True},
        ],
    },

    # ── 5. RICE ─────────────────────────────────────────────────────────────
    "rice": {
        "blinkit": [
            {"name": "Daawat Rozana Super Basmati Rice", "brand": "Daawat",     "quantity": "5 kg",  "price": 380, "mrp": 450, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/14981a.jpg", "in_stock": True},
            {"name": "India Gate Basmati Rice Daily Feast","brand": "India Gate","quantity": "1 kg",  "price": 88,  "mrp": 105, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/12093a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Daawat Rozana Super Basmati Rice",       "brand": "Daawat",     "quantity": "5kg",  "price": 375, "mrp": 450, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/daawat_rozana_5kg.png", "in_stock": True},
            {"name": "India Gate Daily Feast Basmati Rice",    "brand": "India Gate", "quantity": "1 kg", "price": 90,  "mrp": 105, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/india_gate_1kg.png",     "in_stock": True},
        ],
    },

    # ── 6. COOKING OIL & GHEE ───────────────────────────────────────────────
    "oil": {
        "blinkit": [
            {"name": "Fortune Sunlite Refined Sunflower Oil",       "brand": "Fortune",  "quantity": "1 L", "price": 135, "mrp": 165, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/12390a.jpg", "in_stock": True},
            {"name": "Saffola Gold Pro Healthy Lifestyle Edible Oil","brand": "Saffola",  "quantity": "1 L", "price": 155, "mrp": 190, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/12391a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Fortune Sunlite Refined Sunflower Oil Pouch", "brand": "Fortune",  "quantity": "1L",  "price": 132, "mrp": 165, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/fortune_sunlite_1l.png", "in_stock": True},
            {"name": "Saffola Gold Blended Edible Oil",             "brand": "Saffola",  "quantity": "1 L", "price": 159, "mrp": 190, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/saffola_gold_1l.png",    "in_stock": True},
        ],
    },

    # ── 7. PANEER & CURD ────────────────────────────────────────────────────
    "paneer": {
        "blinkit": [
            {"name": "Amul Fresh Malai Paneer",     "brand": "Amul",        "quantity": "200 g", "price": 92, "mrp": 95, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/1841a.jpg", "in_stock": True},
            {"name": "Mother Dairy Classic Paneer", "brand": "Mother Dairy","quantity": "200 g", "price": 90, "mrp": 95, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/1842a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Amul Malai Fresh Paneer Pack",     "brand": "Amul",        "quantity": "200g",  "price": 94, "mrp": 95, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/amul_paneer_200g.png",        "in_stock": True},
            {"name": "Mother Dairy Classic Paneer Block","brand": "Mother Dairy","quantity": "200 g", "price": 89, "mrp": 95, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/mother_dairy_paneer.png",    "in_stock": True},
        ],
    },

    # ── 8. EGGS ─────────────────────────────────────────────────────────────
    "eggs": {
        "blinkit": [
            {"name": "Fresh White Table Eggs",      "brand": "Eggoz", "quantity": "6 pcs",  "price": 52,  "mrp": 60,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/129a.jpg", "in_stock": True},
            {"name": "Fresh White Table Eggs Tray", "brand": "Eggoz", "quantity": "12 pcs", "price": 100, "mrp": 120, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/130a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Farm Fresh White Eggs Pack of 6",  "brand": "Eggoz", "quantity": "6 pcs",  "price": 54, "mrp": 60,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/white_eggs_6pcs.png",  "in_stock": True},
            {"name": "Farm Fresh White Eggs Pack of 12", "brand": "Eggoz", "quantity": "12 pcs", "price": 98, "mrp": 120, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/white_eggs_12pcs.png", "in_stock": True},
        ],
    },

    # ── 9. CHIPS & SNACKS ───────────────────────────────────────────────────
    "chips": {
        "blinkit": [
            {"name": "Lay's India's Magic Masala Potato Chips", "brand": "Lay's", "quantity": "50 g", "price": 20, "mrp": 20, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/540a.jpg", "in_stock": True},
            {"name": "Lay's Classic Salted Potato Chips",       "brand": "Lay's", "quantity": "50 g", "price": 20, "mrp": 20, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/541a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Lay's Magic Masala Chips",   "brand": "Lay's", "quantity": "50g",   "price": 20, "mrp": 20, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/lays_magic_masala.png", "in_stock": True},
            {"name": "Lay's Classic Salted Crisps","brand": "Lay's", "quantity": "50 g",  "price": 20, "mrp": 20, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/lays_salted.png",       "in_stock": True},
        ],
    },

    # ── 10. CHOCOLATE ───────────────────────────────────────────────────────
    "chocolate": {
        "blinkit": [
            {"name": "Cadbury Dairy Milk Chocolate Bar",      "brand": "Cadbury", "quantity": "50 g", "price": 45, "mrp": 45, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/320a.jpg", "in_stock": True},
            {"name": "Cadbury Dairy Milk Silk Chocolate Bar", "brand": "Cadbury", "quantity": "60 g", "price": 80, "mrp": 85, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/321a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Cadbury Dairy Milk Bar",      "brand": "Cadbury", "quantity": "50g",   "price": 45, "mrp": 45, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/dairy_milk.png",      "in_stock": True},
            {"name": "Cadbury Dairy Milk Silk Bar", "brand": "Cadbury", "quantity": "60 g",  "price": 82, "mrp": 85, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/dairy_milk_silk.png", "in_stock": True},
        ],
    },

    # ── 11. BISCUITS ────────────────────────────────────────────────────────
    "biscuit": {
        "blinkit": [
            {"name": "Parle-G Original Glucose Biscuits",  "brand": "Parle", "quantity": "250 g", "price": 25, "mrp": 25, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/102a.jpg", "in_stock": True},
            {"name": "Cadbury Oreo Vanilla Creme Biscuit", "brand": "Oreo",  "quantity": "120 g", "price": 35, "mrp": 35, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/103a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Parle-G Glucose Biscuits Pack",          "brand": "Parle", "quantity": "250g",  "price": 25, "mrp": 25, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/parle_g.png", "in_stock": True},
            {"name": "Oreo Vanilla Creme Sandwich Cookies",    "brand": "Oreo",  "quantity": "120 g", "price": 34, "mrp": 35, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/oreo.png",   "in_stock": True},
        ],
    },

    # ── 12. COFFEE ──────────────────────────────────────────────────────────
    "coffee": {
        "blinkit": [
            {"name": "Nescafe Classic Instant Coffee Jar", "brand": "Nescafe", "quantity": "50 g", "price": 195, "mrp": 215, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/230a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Nescafe Classic Coffee Jar", "brand": "Nescafe", "quantity": "50g", "price": 190, "mrp": 215, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/nescafe.png", "in_stock": True},
        ],
    },

    # ── 13. TEA ─────────────────────────────────────────────────────────────
    "tea": {
        "blinkit": [
            {"name": "Brooke Bond Red Label Tea Pouch", "brand": "Red Label", "quantity": "500 g", "price": 250, "mrp": 285, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/330a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Brooke Bond Red Label Leaf Tea", "brand": "Red Label", "quantity": "500g", "price": 245, "mrp": 285, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/red_label.png", "in_stock": True},
        ],
    },

    # ── 14. COLD DRINKS ─────────────────────────────────────────────────────
    "coke": {
        "blinkit": [
            {"name": "Coca-Cola Soft Drink Can",        "brand": "Coca-Cola", "quantity": "300 ml", "price": 40, "mrp": 40, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/324a.jpg", "in_stock": True},
            {"name": "Coca-Cola Diet Coke Soft Drink",  "brand": "Coca-Cola", "quantity": "300 ml", "price": 40, "mrp": 40, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/325a.jpg", "in_stock": True},
            {"name": "Coca-Cola Soft Drink Bottle",     "brand": "Coca-Cola", "quantity": "750 ml", "price": 45, "mrp": 45, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/326a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Coca-Cola Soft Drink Can",           "brand": "Coca-Cola", "quantity": "300ml",  "price": 38, "mrp": 40, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/coke_can_300ml.png",    "in_stock": True},
            {"name": "Coca-Cola Zero Sugar Soft Drink Can","brand": "Coca-Cola", "quantity": "300 ml", "price": 40, "mrp": 40, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/coke_zero_can.png",      "in_stock": True},
            {"name": "Coca-Cola Soft Drink - 750 ml Bottle","brand":"Coca-Cola", "quantity": "750 ml", "price": 45, "mrp": 45, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/coke_750ml.png",         "in_stock": True},
        ],
    },

    # ── 15. BREAD ───────────────────────────────────────────────────────────
    "bread": {
        "blinkit": [
            {"name": "Britannia 100% Whole Wheat Brown Bread","brand": "Britannia", "quantity": "400 g", "price": 50, "mrp": 55, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/105a.jpg", "in_stock": True},
            {"name": "Britannia Daily White Bread",            "brand": "Britannia", "quantity": "400 g", "price": 40, "mrp": 45, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/106a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Britannia 100% Whole Wheat Bread", "brand": "Britannia",    "quantity": "400g",  "price": 52, "mrp": 55, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/britannia_wheat_bread.png", "in_stock": True},
            {"name": "Britannia White Sliced Bread",     "brand": "Britannia",    "quantity": "400 g", "price": 42, "mrp": 45, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/britannia_white_bread.png", "in_stock": True},
            {"name": "English Oven Sandwich Bread",      "brand": "English Oven", "quantity": "400 g", "price": 48, "mrp": 50, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/english_oven_bread.png",   "in_stock": True},
        ],
    },

    # ── 16. SALT ────────────────────────────────────────────────────────────
    "salt": {
        "blinkit": [
            {"name": "Tata Salt Vacuum Evaporated Iodised Salt", "brand": "Tata Salt", "quantity": "1 kg", "price": 28, "mrp": 30, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/120a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Tata Iodised Salt", "brand": "Tata Salt", "quantity": "1kg", "price": 28, "mrp": 30, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/tata_salt_1kg.png", "in_stock": True},
        ],
    },

    # ── 17. VEGETABLES ──────────────────────────────────────────────────────
    "onion": {
        "blinkit": [
            {"name": "Fresh Onion (Pyaz)", "brand": "Fresh Produce", "quantity": "1 kg", "price": 34, "mrp": 45, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/150a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Fresh Onion", "brand": "Fresh Produce", "quantity": "1kg", "price": 32, "mrp": 45, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/onion_1kg.png", "in_stock": True},
        ],
    },
    "potato": {
        "blinkit": [
            {"name": "Fresh Potato (Aloo)", "brand": "Fresh Produce", "quantity": "1 kg", "price": 28, "mrp": 35, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/151a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Fresh Potato", "brand": "Fresh Produce", "quantity": "1kg", "price": 30, "mrp": 35, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/potato_1kg.png", "in_stock": True},
        ],
    },

    # ── 18. PERSONAL CARE ───────────────────────────────────────────────────
    "dettol": {
        "blinkit": [
            {"name": "Dettol Original Liquid Handwash Refill", "brand": "Dettol", "quantity": "675 ml", "price": 99,  "mrp": 119, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/401a.jpg", "in_stock": True},
            {"name": "Dettol Original Bathing Soap Bar",        "brand": "Dettol", "quantity": "125 g",  "price": 55,  "mrp": 60,  "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/402a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Dettol Original Handwash Liquid Refill Pouch", "brand": "Dettol", "quantity": "675ml", "price": 104, "mrp": 119, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/dettol_handwash.png", "in_stock": True},
            {"name": "Dettol Bathing Soap - Original",               "brand": "Dettol", "quantity": "125g",  "price": 54,  "mrp": 60,  "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/dettol_soap.png",     "in_stock": True},
        ],
    },
    "colgate": {
        "blinkit": [
            {"name": "Colgate Strong Teeth Dental Cream Toothpaste", "brand": "Colgate", "quantity": "150 g", "price": 105, "mrp": 120, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/501a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Colgate Strong Teeth Toothpaste", "brand": "Colgate", "quantity": "150g", "price": 108, "mrp": 120, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/colgate_150g.png", "in_stock": True},
        ],
    },
    "surf": {
        "blinkit": [
            {"name": "Surf Excel Easy Wash Detergent Powder", "brand": "Surf Excel", "quantity": "1 kg", "price": 145, "mrp": 160, "image": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=270/app/images/products/sliding_image/601a.jpg", "in_stock": True},
        ],
        "instamart": [
            {"name": "Surf Excel Easy Wash Washing Powder", "brand": "Surf Excel", "quantity": "1kg", "price": 142, "mrp": 160, "image": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/rng/md/carousel/production/surf_excel_1kg.png", "in_stock": True},
        ],
    },

    # ── ALIASES ─────────────────────────────────────────────────────────────
    "noodles":    None,  # resolved below
    "amul":       None,
    "dairy":      None,
    "wheat":      None,
    "flour":      None,
    "basmati":    None,
    "chawal":     None,
    "ghee":       None,
    "sunflower":  None,
    "curd":       None,
    "eggs":       None,
    "snack":      None,
    "kurkure":    None,
    "wafer":      None,
    "candy":      None,
    "cookie":     None,
    "rusk":       None,
    "chai":       None,
    "cola":       None,
    "pepsi":      None,
    "soda":       None,
    "drink":      None,
    "pyaz":       None,
    "aloo":       None,
    "soap":       None,
    "toothpaste": None,
    "detergent":  None,
    "tide":       None,
}

# Resolve aliases
_ALIASES: dict = {
    "noodles": "maggi",  "yippee": "maggi",    "ramen": "maggi",
    "amul": "butter",    "dairy": "butter",
    "wheat": "atta",     "flour": "atta",       "aashirvaad": "atta",
    "basmati": "rice",   "chawal": "rice",      "daawat": "rice",
    "ghee": "oil",       "sunflower": "oil",    "mustard": "oil",
    "curd": "paneer",
    "egg": "eggs",       "anda": "eggs",
    "snack": "chips",    "kurkure": "chips",    "wafer": "chips",    "namkeen": "chips",
    "candy": "chocolate","silk": "chocolate",   "kitkat": "chocolate",
    "cookie": "biscuit", "rusk": "biscuit",
    "chai": "tea",       "chaai": "tea",
    "cola": "coke",      "pepsi": "coke",       "soda": "coke",      "drink": "coke",
    "pyaz": "onion",
    "aloo": "potato",
    "soap": "dettol",    "sanitizer": "dettol", "wash": "dettol",
    "toothpaste": "colgate", "brush": "colgate","paste": "colgate",  "oral": "colgate",
    "detergent": "surf", "tide": "surf",        "ariel": "surf",
}
# Fill alias entries
for alias, target in _ALIASES.items():
    PAIRED_CATALOG[alias] = PAIRED_CATALOG.get(target)


def _resolve_key(query: str) -> str | None:
    """Find the best matching catalog key for an arbitrary query string."""
    q = query.lower().strip()
    # Direct match
    if q in PAIRED_CATALOG and PAIRED_CATALOG[q]:
        return q
    # Substring match: query contains key or key contains query
    for key in PAIRED_CATALOG:
        if not PAIRED_CATALOG[key]:
            continue
        if key in q or q in key:
            return key
    # Word-level match
    words = set(q.split())
    for key in PAIRED_CATALOG:
        if not PAIRED_CATALOG[key]:
            continue
        if set(key.split()) & words:
            return key
    return None


def _tag(items: list, source_name: str) -> list:
    return [{**item, "is_sample": True, "source": source_name} for item in items]


def get_mock_items(query: str) -> list:
    """Return sample Instamart items for the query (legacy API used by app.py)."""
    key = _resolve_key(query)
    if key and PAIRED_CATALOG.get(key):
        return _tag(PAIRED_CATALOG[key]["instamart"], "sampleData.ts")
    return []


def get_mock_blinkit_items(query: str) -> list:
    """Return sample Blinkit items for the query (new API)."""
    key = _resolve_key(query)
    if key and PAIRED_CATALOG.get(key):
        return _tag(PAIRED_CATALOG[key]["blinkit"], "sampleData.ts")
    return []


def get_mock_paired(query: str) -> dict:
    """Return both platforms' fixture items for a query."""
    key = _resolve_key(query)
    if key and PAIRED_CATALOG.get(key):
        pair = PAIRED_CATALOG[key]
        return {
            "blinkit": _tag(pair["blinkit"], "sampleData.ts"),
            "instamart": _tag(pair["instamart"], "sampleData.ts"),
        }
    return {"blinkit": [], "instamart": []}
