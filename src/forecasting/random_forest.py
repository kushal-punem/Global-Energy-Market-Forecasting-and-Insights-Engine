import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.forecasting.features import load_wti_data, create_features


def main():
    print("=" * 60)
    print("WTI RANDOM FOREST FORECASTING MODEL")
    print("=" * 60)

    # Load data
    print("\nLoading WTI data...")
    df = load_wti_data()

    # Feature engineering
    print("Creating features...")
    df = create_features(df)

    feature_columns = [
        "lag_1",
        "lag_7",
        "lag_30",
        "rolling_mean_7",
        "rolling_mean_30",
        "rolling_std_30",
        "year",
        "month",
        "day_of_week",
    ]

    X = df[feature_columns]
    y = df["price"]

    # Time-series split
    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print(f"\nTraining records: {len(X_train)}")
    print(f"Testing records:  {len(X_test)}")

    # Train Random Forest
    print("\nTraining Random Forest...")

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # Predictions
    predictions = model.predict(X_test)

    # Evaluation
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    print("\n" + "=" * 60)
    print("RANDOM FOREST PERFORMANCE")
    print("=" * 60)

    print(f"MAE:  ${mae:.2f}")
    print(f"RMSE: ${rmse:.2f}")

    # Feature importance
    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_,
    }).sort_values(
        "importance",
        ascending=False
    )

    print("\nFeature importance:")
    print(importance.to_string(index=False))

    # Sample predictions
    results = pd.DataFrame({
        "date": df.iloc[split_index:]["date"].values,
        "actual_price": y_test.values,
        "predicted_price": predictions,
    })

    print("\nSample predictions:")
    print(results.head(10).to_string(index=False))

    print("\nRandom Forest model completed successfully.")


if __name__ == "__main__":
    main()