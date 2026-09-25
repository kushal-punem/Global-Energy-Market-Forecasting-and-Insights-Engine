import pandas as pd
import matplotlib.pyplot as plt

from src.database.db import get_engine
from src.forecasting.features import create_features
from src.forecasting.model import FEATURES, train_model


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


def main():

    print("=" * 60)
    print("WTI FORECAST MODEL EVALUATION")
    print("=" * 60)

    # Load data
    df = load_data()

    # Create features
    df = create_features(df)
    df = df.dropna().reset_index(drop=True)

    X = df[FEATURES]
    y = df["price"]

    # Time-based split
    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    dates_test = df["date"].iloc[split_index:]

    # Train
    print("\nTraining model...")

    model = train_model(
        X_train,
        y_train,
    )

    # Predict
    predictions = model.predict(X_test)

    results = pd.DataFrame({
        "date": dates_test.values,
        "actual": y_test.values,
        "predicted": predictions,
    })

    print("\nEvaluation sample:")
    print(results.tail(10).to_string(index=False))

    # Save results
    results.to_csv(
        "data/forecasts/forecast_evaluation.csv",
        index=False,
    )

    print("\nSaved:")
    print("data/forecasts/forecast_evaluation.csv")

    # Plot
    plt.figure(figsize=(14, 6))

    plt.plot(
        results["date"],
        results["actual"],
        label="Actual Price",
    )

    plt.plot(
        results["date"],
        results["predicted"],
        label="Predicted Price",
    )

    plt.xlabel("Date")
    plt.ylabel("WTI Price ($/BBL)")
    plt.title("WTI Actual vs Predicted Prices")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        "data/forecasts/actual_vs_predicted.png",
        dpi=150,
    )

    print("Saved:")
    print("data/forecasts/actual_vs_predicted.png")

    print("\nEvaluation completed.")


if __name__ == "__main__":
    main()