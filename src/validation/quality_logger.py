from sqlalchemy import text

from src.database.db import get_engine


def log_quality_run(
    commodity: str,
    records_received: int,
    missing_values: int,
    duplicate_records: int,
    negative_prices: int,
    status: str,
) -> None:
    """Store data-quality results in PostgreSQL."""

    query = text(
        """
        INSERT INTO data_quality_logs
        (
            commodity,
            records_received,
            missing_values,
            duplicate_records,
            negative_prices,
            status
        )
        VALUES
        (
            :commodity,
            :records_received,
            :missing_values,
            :duplicate_records,
            :negative_prices,
            :status
        );
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "commodity": commodity,
                "records_received": records_received,
                "missing_values": missing_values,
                "duplicate_records": duplicate_records,
                "negative_prices": negative_prices,
                "status": status,
            },
        )

    print("✓ Data-quality result saved to PostgreSQL")