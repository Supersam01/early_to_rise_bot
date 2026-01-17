import os
from datetime import datetime

# --- ADMIN & TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8397097729:AAE7eextZCH1DuqMjyNjxhPy2t1OqxO7HJo")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8251843110"))
ADMIN_USERNAME = "@early_to_rise"

# --- DATES & TIMES ---
# Bot is active only between these dates
START_DATE = datetime(2026, 1, 16)
END_DATE = datetime(2026, 2, 28)

# --- BUSINESS RULES ---
PACKAGING_FEE = 200
STOCK_LIMIT_PER_DAY = 10

# --- HOSTELS (Delivery Priority) ---
HOSTELS = [
    "Dorcas", "Deborah", "Lydia", "Mary", "Daniel",
    "Joseph", "Paul", "Peter", "Esther", "John"
]

# --- MENUS ---

# COMBO A: 1 Liquid + 2 Solids
# Only these specific items are available for Combo A
MENU_A = {
    "liquid": {
        "Hot Chocolate with Whipped Cream": 2200,
        "Vanilla Milkshake": 2200,
        "Pineapple Parfait": 2800,
        "Apple Parfait": 2800,
        "Mixed Fruits Parfait": 3300,
        "Cookies and Cream Parfait": 3300
    },
    "solid": {
        "Pancakes, Egg and Syrup": 700,
        "Banana Pancakes": 500,
        "Plain Pancakes": 300,
        "Waffles, Egg and Syrup": 800,
        "Plain Waffles": 400,
        "Egg Toast": 400,
        "Yamarita & Egg Sauce": 1800, # Mapped "Egg Sauce" to Yamarita based on price list
        "Chicken Sauce Sandwich": 500,
        "Plain Donut": 600,
        "Donut Waffles": 900,
        "Sausage Roll": 600,
        "Egg Roll": 700
    }
}

# COMBO B: 1 Liquid + 1 Solid
# Only these specific items are available for Combo B
MENU_B = {
    "liquid": {
        "Black Coffee": 500,
        "Hot Coffee": 600,
        "Hot Chocolate": 600,
        "Coffee Banana Smoothie": 1100,
        "Banana Piney Smoothie": 600,
        "Banana Milkshake": 1400,
        "Chocolate Milkshake": 900,
        "Coffee Milkshake": 1400,
        "Oreos Milkshake": 1400
    },
    "solid": {
        "Pancakes, Eggs, Syrup and Sausage": 1100,
        "Pancakes, Eggs, Syrup and Chicken": 2200,
        "Waffles, Eggs, Syrup and Chicken": 2800,
        "Waffles, Eggs, Sausage, Syrup": 1300,
        "French Toast": 1700,
        "Egg & Chicken Sandwich": 1400,
        "Suya Stir Fry Spaghetti": 1400,
        "White Spaghetti & Sauce": 900,
        "Glazed Donut": 1400
    }
}

# --- COMBO RULES CONFIGURATION ---
COMBO_CONFIG = {
    "A": {
        "req_liquid": 1,
        "req_solid": 2,
        "menu": MENU_A,
        "desc": "1 Liquid + 2 Solids"
    },
    "B": {
        "req_liquid": 1,
        "req_solid": 1,
        "menu": MENU_B,
        "desc": "1 Liquid + 1 Solid"
    }
}

