import sqlite3
from datetime import datetime

DB_NAME = "price_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            price REAL,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_price(product, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prices (product, price, time)
        VALUES (?, ?, ?)
    """, (product, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_last_price(product):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT price FROM prices
        WHERE product = ?
        ORDER BY id DESC
        LIMIT 1
    """, (product,))

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None