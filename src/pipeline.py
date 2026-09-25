from pathlib import Path

from src.database.loader import load_wti_data
from src.ingestion.api_client import EIAClient
from src.ingestion.data_loader import response_to_dataframe
from src.validation.quality_logger import log_quality_run
from src.validation.validator import validate_dataset


OUTPUT_PATH = Path("data/raw/wti.csv")


def run_pipeline() -> None:
    """Run the complete WTI ETL pipeline."""

    print("=" * 60)
    print("GLOBAL ENERGY MARKET ENGINE")
    print("WTI ETL PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Extract
    # ---------------------------------------------------------

    print("\n[1/5] Extracting WTI data...")

    client = EIAClient()

    data = client.get_series(
        series_id="PET.RWTC.D",
        start_date="2006-01-01",
        end_date="2026-09-22",
    )

    # ---------------------------------------------------------
    # 2. Transform
    # ---------------------------------------------------------

    print("\n[2/5] Transforming data...")

    df = response_to_dataframe(data)

    print(f"Records received: {len(df)}")

    # ---------------------------------------------------------
    # 3. Validate
    # ---------------------------------------------------------

    print("\n[3/5] Validating data...")

    validate_dataset(df)

    negative_prices = int(
        (df["price"] < 0).sum()
    )

    missing_values = int(
        df.isna().sum().sum()
    )

    duplicate_records = int(
        df["date"].duplicated().sum()
    )

    # ---------------------------------------------------------
    # 4. Save raw data
    # ---------------------------------------------------------

    print("\n[4/5] Saving raw data...")

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(f"Saved to: {OUTPUT_PATH}")

    # ---------------------------------------------------------
    # 5. Load PostgreSQL
    # ---------------------------------------------------------

    print("\n[5/5] Loading PostgreSQL...")

    inserted = load_wti_data()

    # ---------------------------------------------------------
    # Quality log
    # ---------------------------------------------------------

    log_quality_run(
        commodity="WTI Crude Oil",
        records_received=len(df),
        missing_values=missing_values,
        duplicate_records=duplicate_records,
        negative_prices=negative_prices,
        status="SUCCESS",
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(f"API records:      {len(df)}")
    print(f"DB rows inserted: {inserted}")
    print(f"Negative prices:  {negative_prices}")


if __name__ == "__main__":
    run_pipeline()