from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.db import get_engine


CSV_PATH = Path("data/raw/wti.csv")

def load_wti_data() -> int:
    """Load WTI CSV data into PostgreSQL."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {CSV_PATH}"
        )

    print(f"Reading data from: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    print(f"Records read from CSV: {len(df)}")

    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["source"] = "EIA"

    df = df[
        [
            "date",
            "commodity",
            "description",
            "price",
            "unit",
            "source",
        ]
    ]

    engine = get_engine()

    insert_query = text(
        """
        INSERT INTO market_prices
        (
            date,
            commodity,
            description,
            price,
            unit,
            source
        )
        VALUES
        (
            :date,
            :commodity,
            :description,
            :price,
            :unit,
            :source
        )
        ON CONFLICT (date, commodity)
        DO NOTHING;
        """
    )

    inserted = 0

    with engine.begin() as connection:

        for row in df.to_dict(orient="records"):

            result = connection.execute(
                insert_query,
                row
            )

            inserted += result.rowcount

    skipped = len(df) - inserted

    print(f"Records inserted: {inserted}")
    print(f"Records skipped: {skipped}")

    return inserted

if __name__ == "__main__":
    load_wti_data()