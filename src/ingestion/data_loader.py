import pandas as pd


def response_to_dataframe(data: dict) -> pd.DataFrame:
    """
    Convert an EIA API response into a normalized DataFrame.
    """

    records = data.get("response", {}).get("data", [])

    if not records:
        raise ValueError("No data found in EIA API response.")

    df = pd.DataFrame(records)

    # Keep only the columns needed for our project
    df = df[
        [
            "period",
            "product-name",
            "series-description",
            "value",
            "units",
        ]
    ]

    # Rename columns to our project naming convention
    df = df.rename(
        columns={
            "period": "date",
            "product-name": "commodity",
            "series-description": "description",
            "value": "price",
            "units": "unit",
        }
    )

    # Convert data types
    df["date"] = pd.to_datetime(df["date"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    return df