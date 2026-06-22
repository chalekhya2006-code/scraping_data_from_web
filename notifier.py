import smtplib
from email.mime.text import MIMEText

EMAIL = "chalekhya2006@gmail.com"
PASSWORD = "eezp gapa iyrc xrpv"
TO_EMAIL = "chalekhya2006@gmail.com"

def send_email(product, old_price, new_price, drop_percent):

    subject = f"🔥 Price Drop Alert: {product}"

    body = f"""
🔥 AMAZON PRICE DROP ALERT

Product: {product}

Old Price: ₹{old_price}
New Price: ₹{new_price}

📉 Drop: {drop_percent:.2f}%

💡 Tip: This may be a good time to buy!
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("📧 Email sent successfully!")

    except Exception as e:
        print("❌ Email failed:", e)