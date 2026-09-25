import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-series features for WTI price forecasting.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    # Calendar features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

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

    return df