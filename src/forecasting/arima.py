import os

import numpy as np
import pandas as pd
from sqlalchemy import text
from statsmodels.tsa.arima.model import ARIMA

from src.database.db import get_engine


COMMODITY = "WTI Crude Oil"


def load_wti_data() -> pd.DataFrame:
    """Load WTI historical prices from PostgreSQL."""

    query = """
        SELECT
            date,
            price
        FROM market_prices
        WHERE commodity = :commodity
        ORDER BY date;
    """

    engine = get_engine()

    with engine.connect() as connection:
        df = pd.read_sql(
            text(query),
            connection,
            params={"commodity": COMMODITY},
        )

    df["date"] = pd.to_datetime(df["date"])
    df["price"] = pd.to_numeric(df["price"])

    return df


def calculate_metrics(actual, predicted):
    """Calculate forecasting evaluation metrics."""

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mae = np.mean(np.abs(actual - predicted))

    rmse = np.sqrt(
        np.mean((actual - predicted) ** 2)
    )

    non_zero = actual != 0

    mape = (
        np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        )
        * 100
    )

    return mae, rmse, mape


def main():

    print("=" * 60)
    print("WTI ARIMA FORECASTING")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load data
    # ---------------------------------------------------------

    print("\n[1/5] Loading historical data...")

    df = load_wti_data()

    print(f"Records loaded: {len(df)}")

    # ---------------------------------------------------------
    # 2. Prepare time series
    # ---------------------------------------------------------

    print("\n[2/5] Preparing time series...")

    df = df.sort_values("date")

    prices = df["price"].values

    split_index = int(len(prices) * 0.80)

    train = prices[:split_index]
    test = prices[split_index:]

    test_dates = df["date"].iloc[split_index:].reset_index(drop=True)

    print(f"Training records: {len(train)}")
    print(f"Testing records:  {len(test)}")

    # ---------------------------------------------------------
    # 3. Train ARIMA
    # ---------------------------------------------------------

    print("\n[3/5] Training ARIMA model...")

    model = ARIMA(
        train,
        order=(5, 1, 0),
    )

    fitted_model = model.fit()

    print("ARIMA training completed.")
    print(f"Model: ARIMA(5,1,0)")

    # ---------------------------------------------------------
    # 4. Forecast test period
    # ---------------------------------------------------------

    print("\n[4/5] Generating predictions...")

    predictions = fitted_model.forecast(
        steps=len(test)
    )

    predictions = np.asarray(predictions)

    # ---------------------------------------------------------
    # 5. Evaluate
    # ---------------------------------------------------------

    print("\n[5/5] Evaluating model...")

    mae, rmse, mape = calculate_metrics(
        test,
        predictions,
    )

    print(f"\nMAE:  ${mae:.2f}")
    print(f"RMSE: ${rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")

    evaluation = pd.DataFrame(
        {
            "date": test_dates,
            "actual": test,
            "predicted": predictions,
        }
    )

    os.makedirs(
        "data/forecasts",
        exist_ok=True,
    )

    output_file = (
        "data/forecasts/arima_evaluation.csv"
    )

    evaluation.to_csv(
        output_file,
        index=False,
    )

    print(f"\nSaved:")
    print(output_file)

    print("\n" + "=" * 60)
    print("ARIMA EVALUATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()