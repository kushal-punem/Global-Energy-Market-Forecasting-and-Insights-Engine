from pathlib import Path

import pandas as pd

from src.ingestion.api_client import EIAClient
from src.ingestion.data_loader import response_to_dataframe
from src.validation.validator import validate_dataset
from src.validation.quality_logger import log_quality_run


def main():

    client = EIAClient()

    print("Fetching WTI data from EIA...")

    data = client.get_series(
        series_id="PET.RWTC.D",
        start_date="2006-01-01",
        end_date="2026-09-22",
    )

    print("API request successful.")

    df = response_to_dataframe(data)

    print(f"Records received: {len(df)}")

    # Validate data before saving
    validate_dataset(df)

    negative_prices = int((df["price"] < 0).sum())

    log_quality_run(
        commodity="WTI Crude Oil",
        records_received=len(df),
        missing_values=int(df.isna().sum().sum()),
        duplicate_records=int(df["date"].duplicated().sum()),
        negative_prices=negative_prices,
        status="SUCCESS",
    )

    # Save raw data
    output_path = Path("data/raw/wti.csv")

    df.to_csv(output_path, index=False)

    print(f"\nRaw WTI data saved to: {output_path}")


if __name__ == "__main__":
    main()