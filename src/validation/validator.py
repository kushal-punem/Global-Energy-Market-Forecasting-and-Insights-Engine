import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "commodity",
    "description",
    "price",
    "unit",
}


def validate_columns(df: pd.DataFrame) -> None:
    """Validate that all required columns exist."""

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_dates(df: pd.DataFrame) -> None:
    """Validate date values."""

    if df["date"].isna().any():
        raise ValueError("Dataset contains missing dates.")

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        raise ValueError("Date column is not in datetime format.")


def validate_prices(df: pd.DataFrame) -> None:
    """Validate price values."""

    if df["price"].isna().any():
        raise ValueError("Dataset contains missing prices.")

    if not pd.api.types.is_numeric_dtype(df["price"]):
        raise ValueError("Price column is not numeric.")

    # Negative WTI prices are historically valid.
    # WTI traded below zero during the April 2020 market shock.
    negative_count = (df["price"] < 0).sum()

    if negative_count > 0:
        print(
            f"⚠ Warning: {negative_count} negative price observations found."
        )
        print(
            "  Negative WTI prices are retained because they are "
            "historically valid observations."
        )


def validate_duplicates(df: pd.DataFrame) -> None:
    """Check for duplicate dates."""

    duplicate_count = df["date"].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Dataset contains {duplicate_count} duplicate dates."
        )


def validate_sorted_dates(df: pd.DataFrame) -> None:
    """Check that dates are sorted chronologically."""

    if not df["date"].is_monotonic_increasing:
        raise ValueError("Dates are not sorted chronologically.")


def validate_dataset(df: pd.DataFrame) -> None:
    """Run all validation checks."""

    print("Running data-quality checks...\n")

    validate_columns(df)
    print("✓ Column validation passed")

    validate_dates(df)
    print("✓ Date validation passed")

    validate_prices(df)
    print("✓ Price validation passed")

    validate_duplicates(df)
    print("✓ Duplicate validation passed")

    validate_sorted_dates(df)
    print("✓ Date ordering validation passed")

    print("\nAll validation checks passed.")