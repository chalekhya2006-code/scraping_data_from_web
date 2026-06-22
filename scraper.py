
import requests
from bs4 import BeautifulSoup
import sqlite3
import schedule
import time
from datetime import datetime

DB = "price_tracker.db"

# Products to track
PRODUCTS_TO_TRACK = [
    {
        "name": "iPhone 15 - Amazon",
        "url": "https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX1W1XY",
        "store": "amazon"
    },
    {
        "name": "Samsung S23 - Flipkart",
        "url": "https://www.flipkart.com/",
        "store": "flipkart"
    }
]


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            price REAL,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_price(url, store):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        if store == "amazon":

            price_element = soup.find(
                "span",
                class_="a-price-whole"
            )

            if price_element:
                price = (
                    price_element.text
                    .replace(",", "")
                    .replace(".", "")
                )
                return float(price)

        elif store == "flipkart":

            price_element = soup.find(
                "div",
                class_="Nx9bqj"
            )

            if price_element:
                price = (
                    price_element.text
                    .replace("₹", "")
                    .replace(",", "")
                )
                return float(price)

    except Exception as e:
        print(f"Error fetching price: {e}")

    return None


def save_price(product, price):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    c.execute(
        """
        INSERT INTO prices
        (product, price, time)
        VALUES (?, ?, ?)
        """,
        (product, price, now)
    )

    conn.commit()
    conn.close()


def track_and_update():

    print(
        f"\nTracking started at "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    for item in PRODUCTS_TO_TRACK:

        price = get_price(
            item["url"],
            item["store"]
        )

        if price:

            save_price(
                item["name"],
                price
            )

            print(
                f"✅ Updated "
                f"{item['name']} : ₹{price}"
            )

        else:

            print(
                f"❌ Failed to fetch "
                f"{item['name']}"
            )


# Initialize Database
init_db()

# Run once immediately
track_and_update()

# Run every 2 hours
schedule.every(2).hours.do(
    track_and_update
)

print(
    "\n⏳ Price Tracker running..."
    "\nPress CTRL + C to stop."
)

while True:
    schedule.run_pending()
    time.sleep(1)

