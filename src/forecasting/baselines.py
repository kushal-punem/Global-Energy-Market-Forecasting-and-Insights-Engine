import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.database.db import get_engine


def load_data():

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
        return pd.read_sql_query(query, connection)


def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    return mae, rmse


def main():

    print("=" * 60)
    print("WTI BASELINE MODEL COMPARISON")
    print("=" * 60)

    df = load_data()

    prices = df["price"]

    split_index = int(len(df) * 0.8)

    train = prices.iloc[:split_index]
    test = prices.iloc[split_index:]

    # ---------------------------------------------------------
    # Model 1: Naive forecast
    # ---------------------------------------------------------

    last_training_price = train.iloc[-1]

    naive_predictions = np.full(
        len(test),
        last_training_price,
    )

    naive_mae, naive_rmse = calculate_metrics(
        test,
        naive_predictions,
    )

    # ---------------------------------------------------------
    # Model 2: Moving average
    # ---------------------------------------------------------

    window = 30

    moving_average_prediction = train.tail(
        window
    ).mean()

    moving_average_predictions = np.full(
        len(test),
        moving_average_prediction,
    )

    ma_mae, ma_rmse = calculate_metrics(
        test,
        moving_average_predictions,
    )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    results = pd.DataFrame({
        "model": [
            "Naive",
            "30-Day Moving Average",
        ],
        "MAE": [
            naive_mae,
            ma_mae,
        ],
        "RMSE": [
            naive_rmse,
            ma_rmse,
        ],
    })

    print("\nBaseline Results")
    print("-" * 60)

    print(
        results.to_string(
            index=False,
            formatters={
                "MAE": "{:.2f}".format,
                "RMSE": "{:.2f}".format,
            },
        )
    )

    print("\nRandom Forest from previous evaluation:")
    print("MAE  ≈ $1.44")
    print("RMSE ≈ $2.40")

    print("\nComparison completed.")


if __name__ == "__main__":
    main()