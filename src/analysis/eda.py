import os

import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from dotenv import load_dotenv


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "energy_market"),
    "user": os.getenv("DB_USER", "urluser"),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ------------------------------------------------------------
# Database connection
# ------------------------------------------------------------

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ------------------------------------------------------------
# Load daily prices
# ------------------------------------------------------------

def load_daily_prices():
    query = """
        SELECT
            date,
            price
        FROM wti_daily
        ORDER BY date;
    """

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)

    df["date"] = pd.to_datetime(df["date"])

    return df


# ------------------------------------------------------------
# Basic statistics
# ------------------------------------------------------------

def basic_statistics(df):
    print("\n" + "=" * 60)
    print("WTI BASIC STATISTICS")
    print("=" * 60)

    print(f"Records: {len(df):,}")
    print(f"Start date: {df['date'].min().date()}")
    print(f"End date:   {df['date'].max().date()}")

    print(f"\nAverage price: ${df['price'].mean():.2f}")
    print(f"Minimum price: ${df['price'].min():.2f}")
    print(f"Maximum price: ${df['price'].max():.2f}")

    print("\nDescriptive statistics:")
    print(df["price"].describe())


# ------------------------------------------------------------
# Price trend
# ------------------------------------------------------------

def plot_price_trend(df):
    plt.figure(figsize=(14, 6))

    plt.plot(
        df["date"],
        df["price"],
        linewidth=1
    )

    plt.title("WTI Crude Oil Price — Historical Trend")
    plt.xlabel("Date")
    plt.ylabel("Price ($/BBL)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    os.makedirs("data/processed", exist_ok=True)

    plt.savefig(
        "data/processed/wti_price_trend.png",
        dpi=150
    )

    plt.show()


# ------------------------------------------------------------
# Rolling averages
# ------------------------------------------------------------

def plot_rolling_averages(df):
    df = df.copy()

    df["MA30"] = (
        df["price"]
        .rolling(30)
        .mean()
    )

    df["MA90"] = (
        df["price"]
        .rolling(90)
        .mean()
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        df["date"],
        df["price"],
        label="WTI Price",
        linewidth=0.8
    )

    plt.plot(
        df["date"],
        df["MA30"],
        label="30-Day Moving Average",
        linewidth=1.2
    )

    plt.plot(
        df["date"],
        df["MA90"],
        label="90-Day Moving Average",
        linewidth=1.2
    )

    plt.title("WTI Price with Rolling Averages")
    plt.xlabel("Date")
    plt.ylabel("Price ($/BBL)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        "data/processed/wti_rolling_averages.png",
        dpi=150
    )

    plt.show()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("GLOBAL ENERGY MARKET ENGINE")
    print("PYTHON EDA")
    print("=" * 60)

    print("\nLoading WTI data from PostgreSQL...")

    df = load_daily_prices()

    print("Data loaded successfully.")

    basic_statistics(df)

    print("\nGenerating price trend...")
    plot_price_trend(df)

    print("\nGenerating rolling averages...")
    plot_rolling_averages(df)

    print("\nEDA completed successfully.")


if __name__ == "__main__":
    main()