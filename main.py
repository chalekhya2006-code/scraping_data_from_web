from notifier import send_email
import time
from config import PRODUCTS, CHECK_INTERVAL
from scraper import get_price
from database import init_db, save_price, get_last_price

init_db()
print("Database initialized")


def run_tracker():
    for product, url in PRODUCTS.items():

        price = get_price(url)

        if price is None:
            print(f"{product}: Price not found")
            continue

        print(f"{product}: {price}")

        old_price = get_last_price(product)

        # 🔥 FIRST TIME ENTRY
        if old_price is None:
            save_price(product, price)
            print("💾 First entry saved")
            continue

        # 🔥 PRICE DROP LOGIC
        if price < old_price:

            drop = old_price - price
            drop_percent = (drop / old_price) * 100

            print(f"🔥 PRICE DROPPED: {product}")
            print(f"{old_price} → {price}")
            print(f"📉 Drop: {drop_percent:.2f}%")

            send_email(product, old_price, price, drop_percent)

            save_price(product, price)

        # 🔥 PRICE CHANGE (UP or DOWN)
        elif price != old_price:
            save_price(product, price)
            print("💾 Price updated")

        else:
            print(f"✔ No change for {product}")


if __name__ == "__main__":
    while True:
        run_tracker()
        print("Waiting...\n")
        time.sleep(CHECK_INTERVAL)