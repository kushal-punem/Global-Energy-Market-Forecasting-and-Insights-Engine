import pandas as pd

from src.database.db import get_engine
from src.forecasting.features import create_features
from src.forecasting.model import (
    FEATURES,
    train_model,
    evaluate_model,
)


COMMODITY = "WTI Crude Oil"
MODEL_NAME = "RandomForest-v1"


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
        df = pd.read_sql_query(query, connection)

    return df


def save_forecast(forecast_df):
    engine = get_engine()

    rows = forecast_df.to_dict(orient="records")

    insert_query = """
        INSERT INTO forecasts (
            forecast_date,
            commodity,
            predicted_price,
            model
        )
        VALUES (
            :forecast_date,
            :commodity,
            :predicted_price,
            :model
        )
    """

    with engine.begin() as connection:
        for row in rows:
            connection.execute(
                __import__("sqlalchemy").text(insert_query),
                {
                    "forecast_date": row["forecast_date"],
                    "commodity": row["commodity"],
                    "predicted_price": row["predicted_price"],
                    "model": row["model"],
                },
            )


def main():

    print("=" * 60)
    print("WTI PRICE FORECASTING")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load historical data
    # ---------------------------------------------------------

    print("\n[1/6] Loading historical data...")

    df = load_data()

    print(f"Records loaded: {len(df)}")

    # ---------------------------------------------------------
    # 2. Feature engineering
    # ---------------------------------------------------------

    print("\n[2/6] Creating features...")

    df = create_features(df)

    df = df.dropna().reset_index(drop=True)

    print(f"Records after feature creation: {len(df)}")

    # ---------------------------------------------------------
    # 3. Train/test split
    # ---------------------------------------------------------

    print("\n[3/6] Splitting data...")

    X = df[FEATURES]
    y = df["price"]

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print(f"Training records: {len(X_train)}")
    print(f"Testing records:  {len(X_test)}")

    # ---------------------------------------------------------
    # 4. Train model
    # ---------------------------------------------------------

    print("\n[4/6] Training model...")

    model = train_model(
        X_train,
        y_train,
    )

    print("Model training completed.")

    # ---------------------------------------------------------
    # 5. Evaluate
    # ---------------------------------------------------------

    print("\n[5/6] Evaluating model...")

    metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    print(f"MAE:  ${metrics['MAE']:.2f}")
    print(f"RMSE: ${metrics['RMSE']:.2f}")

    # ---------------------------------------------------------
    # 6. Generate future forecast
    # ---------------------------------------------------------

    print("\n[6/6] Generating future forecast...")

    last_date = df["date"].max()
    last_price = df["price"].iloc[-1]

    print(f"Last historical date: {last_date.date()}")
    print(f"Last historical price: ${last_price:.2f}")

    # Number of future trading days
    forecast_days = 30

    history = df[["date", "price"]].copy()

    predictions = []

    for _ in range(forecast_days):

        next_date = history["date"].max() + pd.Timedelta(days=1)

        # Skip weekends
        while next_date.weekday() >= 5:
            next_date += pd.Timedelta(days=1)

        temp = pd.DataFrame({
            "date": history["date"].tolist()
            + [next_date],

            "price": history["price"].tolist()
            + [history["price"].iloc[-1]],
        })

        temp = create_features(temp)

        latest_features = temp.iloc[-1][FEATURES]

        predicted_price = model.predict(
            latest_features.to_frame().T
        )[0]

        predicted_price = max(
            0,
            predicted_price
        )

        predictions.append({
            "forecast_date": next_date.date(),
            "commodity": COMMODITY,
            "predicted_price": round(
                float(predicted_price),
                4,
            ),
            "model": MODEL_NAME,
        })

        # Add prediction to history
        history = pd.concat(
            [
                history,
                pd.DataFrame(
                    [{
                        "date": next_date,
                        "price": predicted_price,
                    }]
                ),
            ],
            ignore_index=True,
        )

    forecast_df = pd.DataFrame(predictions)

    print("\nForecast:")
    print(forecast_df.to_string(index=False))

    # Save
    save_forecast(forecast_df)

    print("\nForecasts saved to PostgreSQL.")

    print("\n" + "=" * 60)
    print("FORECASTING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()