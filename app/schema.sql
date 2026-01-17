-- MENU TABLE
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    profit INTEGER NOT NULL,
    category TEXT NOT NULL,
    stock INTEGER NOT NULL
);

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    hostel TEXT
);

-- ORDERS TABLE
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    hostel TEXT NOT NULL,
    combo_type TEXT NOT NULL,
    packaging_fee INTEGER NOT NULL,
    total_amount INTEGER NOT NULL,
    status TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    reference_code TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CART ITEMS TABLE
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    combo_type TEXT NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(menu_item_id) REFERENCES menu(id)
);

-- STOCK TABLE (optional but good for tracking)
CREATE TABLE IF NOT EXISTS stock (
    menu_item_id INTEGER PRIMARY KEY,
    remaining INTEGER NOT NULL,
    FOREIGN KEY(menu_item_id) REFERENCES menu(id)
);
