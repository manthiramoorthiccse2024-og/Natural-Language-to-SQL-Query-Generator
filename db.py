import sqlite3
from pathlib import Path
from config import settings

def get_connection(readonly=False):
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if readonly:
        conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, timeout=2)
    else:
        conn = sqlite3.connect(str(db_path), timeout=2)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(reset=False):
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if reset and db_path.exists():
        db_path.unlink()
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        city TEXT NOT NULL,
        registration_date TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        order_status TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    """)
    if cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", [
            (1, "Asha Kumar", "Chennai", "2024-01-12"),
            (2, "Ravi Shah", "Mumbai", "2024-02-18"),
            (3, "Meera Iyer", "Chennai", "2024-03-09"),
            (4, "Arjun Das", "Kolkata", "2024-04-21"),
            (5, "Sara Khan", "Bengaluru", "2024-05-04"),
        ])
        cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [
            (1, "Wireless Mouse", "Accessories", 650.0),
            (2, "Mechanical Keyboard", "Accessories", 2400.0),
            (3, "USB-C Hub", "Electronics", 1800.0),
            (4, "Laptop Stand", "Office", 1200.0),
            (5, "Webcam", "Electronics", 3200.0),
        ])
        cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [
            (1, 1, "2025-01-10", "completed"),
            (2, 2, "2025-01-21", "completed"),
            (3, 3, "2025-02-05", "shipped"),
            (4, 4, "2025-02-19", "cancelled"),
            (5, 5, "2025-03-11", "completed"),
            (6, 1, "2025-03-20", "shipped"),
        ])
        cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", [
            (1, 1, 1, 2, 650.0), (2, 1, 2, 1, 2400.0),
            (3, 2, 3, 1, 1800.0), (4, 3, 5, 1, 3200.0),
            (5, 4, 4, 2, 1200.0), (6, 5, 2, 1, 2400.0),
            (7, 5, 1, 3, 650.0), (8, 6, 3, 2, 1800.0),
        ])
    conn.commit()
    conn.close()

def get_schema():
    conn = get_connection(readonly=True)
    schema = {}
    for table in ("customers", "products", "orders", "order_items"):
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        schema[table] = {row["name"]: row["type"] for row in rows}
    conn.close()
    return schema
