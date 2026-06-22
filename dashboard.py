import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
from datetime import datetime, timedelta
import os

DB = "price_tracker.db"

st.set_page_config(page_title="Price Tracker", layout="wide")
st.title("📱 Mobile Price Tracker (From Amazon Reviews Data)")

# ==========================================
# Load mobile names from CSV
# ==========================================
@st.cache_data
def get_mobiles():
    if os.path.exists("Amazon_Mobile_Reviews_Data.csv"):
        try:
            df = pd.read_csv("Amazon_Mobile_Reviews_Data.csv")
            return df['Mobile'].dropna().unique().tolist()
        except:
            pass
    # Default list if CSV not found
    return [
        'Mi 10', 'Apple iPhone 11 Pro', 'OPPO Find X2',
        'OnePlus 7T', 'OnePlus 8 5G', 'Samsung Galaxy M31s',
        'Redmi Note 9 Pro Max', 'Vivo V19',
        'Samsung Galaxy S10 Plus', 'OnePlus 8 Pro'
    ]

mobiles_list = get_mobiles()

# Base prices for mock data
base_prices = {
    'Mi 10': 49999,
    'Apple iPhone 11 Pro': 89900,
    'OPPO Find X2': 64990,
    'OnePlus 7T': 34999,
    'OnePlus 8 5G': 41999,
    'Samsung Galaxy M31s': 19499,
    'Redmi Note 9 Pro Max': 16999,
    'Vivo V19': 24990,
    'Samsung Galaxy S10 Plus': 50999,
    'OnePlus 8 Pro': 54999
}

# ==========================================
# Generate Mock History
# ==========================================
def generate_mock_history():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS prices (product TEXT, price REAL, time TEXT)")
    cursor.execute("DELETE FROM prices")  # Clear old data

    now = datetime.now()
    for prod in mobiles_list:
        base_price = base_prices.get(prod, 25000)  # Default price if not in dict
        # Generate 50 random records within last 365 days
        for _ in range(50):
            random_days_ago = random.randint(1, 365)
            random_date = now - timedelta(days=random_days_ago)
            fluctuation = random.uniform(-0.15, 0.15)
            new_price = round(base_price * (1 + fluctuation), 2)
            cursor.execute(
                "INSERT INTO prices (product, price, time) VALUES (?, ?, ?)",
                (prod, new_price, random_date.strftime("%Y-%m-%d %H:%M:%S"))
            )
    conn.commit()
    conn.close()
    st.success("✅ 1 Year Mock History generated with mobile data! Reloading...")
    st.rerun()

# Sidebar Tools
st.sidebar.header("🛠 Developer Tools")
st.sidebar.info("Click below to generate mock price history using mobiles from CSV")
if st.sidebar.button("Generate Mobile Mock Data"):
    generate_mock_history()
st.sidebar.markdown("---")

# ==========================================
# LOAD AND CLEAN DATA
# ==========================================
conn = sqlite3.connect(DB)
try:
    df = pd.read_sql_query("SELECT * FROM prices", conn)
except:
    df = pd.DataFrame()
conn.close()

if df.empty:
    st.warning("⚠️ No data found in database. Please click 'Generate Mobile Mock Data' in the sidebar.")
    st.stop()

# Fix time + price
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df = df.dropna().sort_values("time")

# Product selection
product = st.sidebar.selectbox("📱 Select Mobile", df["product"].unique())
filtered = df[df["product"] == product].copy()

if filtered.empty:
    st.error("No data available for this mobile")
    st.stop()

filtered['Year'] = filtered['time'].dt.year

# ==========================================
# 📈 STOCK STYLE GRAPH
# ==========================================
st.subheader(f"📈 Price Tracking Line: {product}")
fig, ax = plt.subplots(figsize=(12, 6))

if len(filtered) == 1:
    ax.scatter(filtered["time"], filtered["price"], color="blue", s=100, label="Single Data Point")
else:
    ax.plot(
        filtered["time"],
        filtered["price"],
        linewidth=2.5,
        color="#1f77b4",
        marker="o",
        markersize=4,
        label="Price Trend"
    )

# Year markers
years = filtered['Year'].unique()
y_max = filtered['price'].max()
for year in years:
    year_data = filtered[filtered['Year'] == year]
    if not year_data.empty:
        first_date = year_data['time'].min()
        ax.axvline(x=first_date, color='gray', linestyle='--', alpha=0.7)
        ax.text(first_date, y_max, f' {year}', color='black',
                verticalalignment='bottom', fontweight='bold', fontsize=11)

# Highlight min/max
min_price = filtered["price"].min()
min_time = filtered.loc[filtered["price"].idxmin(), "time"]
ax.scatter(min_time, min_price, color="green", s=80, zorder=5)
ax.annotate(f"Low ₹{min_price}", (min_time, min_price),
            xytext=(0, -20), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="green", lw=1.5), fontweight='bold')

max_price = filtered["price"].max()
max_time = filtered.loc[filtered["price"].idxmax(), "time"]
ax.scatter(max_time, max_price, color="red", s=80, zorder=5)
ax.annotate(f"High ₹{max_price}", (max_time, max_price),
            xytext=(0, 20), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight='bold')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_title(f"{product} Price Timeline")
ax.set_xlabel("Timeline")
ax.set_ylabel("Price (₹)")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend(loc="lower right")
plt.xticks(rotation=45)
st.pyplot(fig)

# ==========================================
# 📊 METRICS & DETAILED HISTORY
# ==========================================
st.subheader("📊 Insights")
current = filtered["price"].iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Current Price", f"₹{current}")
col2.metric("Lowest Price", f"₹{min_price}")
col3.metric("Highest Price", f"₹{max_price}")

st.subheader("📜 Detailed Price History")
history_df = filtered[['time', 'price']].copy()
history_df['Price Change (₹)'] = history_df['price'].diff()
history_df['% Change'] = (history_df['price'].pct_change() * 100).round(2)
history_df = history_df.fillna(0).sort_values('time', ascending=False)
history_df['time'] = history_df['time'].dt.strftime('%d-%b-%Y %I:%M %p')

st.dataframe(
    history_df,
    column_config={
        "time": st.column_config.TextColumn("Date & Time"),
        "price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
        "Price Change (₹)": st.column_config.NumberColumn("Change (₹)", format="%.2f"),
        "% Change": st.column_config.NumberColumn("Change (%)", format="%.2f%%")
    },
    use_container_width=True,
    hide_index=True
)
