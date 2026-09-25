import pandas as pd
from sqlalchemy import text

from src.database.db import get_engine


def load_wti_data() -> pd.DataFrame:
    """Load historical WTI prices from PostgreSQL."""

    query = """
        SELECT
            date,
            price
        FROM market_prices
        WHERE commodity = 'WTI Crude Oil'
        ORDER BY date;
    """

    engine = get_engine()

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-series features for WTI forecasting."""

    df = df.copy()

    # Lag features
    df["lag_1"] = df["price"].shift(1)
    df["lag_7"] = df["price"].shift(7)
    df["lag_30"] = df["price"].shift(30)

    # Rolling averages
    df["rolling_mean_7"] = (
        df["price"]
        .rolling(window=7)
        .mean()
    )

    df["rolling_mean_30"] = (
        df["price"]
        .rolling(window=30)
        .mean()
    )

    # Rolling volatility
    df["rolling_std_30"] = (
        df["price"]
        .rolling(window=30)
        .std()
    )

    # Calendar features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

    # Remove rows created by lag/rolling calculations
    df = df.dropna().reset_index(drop=True)

    return df


def main():
    print("=" * 60)
    print("WTI FEATURE ENGINEERING")
    print("=" * 60)

    print("\nLoading WTI data from PostgreSQL...")
    df = load_wti_data()

    print(f"Records loaded: {len(df)}")

    print("\nCreating forecasting features...")
    feature_df = create_features(df)

    print(f"Records after feature engineering: {len(feature_df)}")

    print("\nFeatures created:")
    for column in feature_df.columns:
        print(f"  ✓ {column}")

    print("\nSample:")
    print(feature_df.tail())

    print("\nFeature engineering completed successfully.")


if __name__ == "__main__":
    main()