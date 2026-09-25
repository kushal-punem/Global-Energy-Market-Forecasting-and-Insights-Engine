import os

import requests
from dotenv import load_dotenv

load_dotenv()


class EIAClient:
    """Client for retrieving energy-market data from the EIA API."""

    BASE_URL = "https://api.eia.gov/v2"

    def __init__(self):
        self.api_key = os.getenv("ENERGY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "ENERGY_API_KEY is not set in the .env file."
            )

    def get_series(
        self,
        series_id,
        start_date=None,
        end_date=None,
        length=5000,
    ):
        """
        Fetch all records for an EIA series using pagination.
        """

        url = f"{self.BASE_URL}/seriesid/{series_id}"

        all_records = []
        offset = 0
        total = None

        while total is None or offset < total:
            params = {
                "api_key": self.api_key,
                "offset": offset,
                "length": length,
            }

            if start_date:
                params["start"] = start_date

            if end_date:
                params["end"] = end_date

            response = requests.get(
                url,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            result = response.json()

            response_data = result.get("response", {})

            records = response_data.get("data", [])

            if total is None:
                total = int(response_data.get("total", 0))

                print(f"Total records available: {total}")

            if not records:
                break

            all_records.extend(records)

            offset += len(records)

            print(f"Fetched {len(all_records)} / {total} records")

        return {
            "response": {
            "data": all_records,
            "total": str(len(all_records)),
        }
        }
    



if __name__ == "__main__":

    client = EIAClient()

    data = client.get_series(
        series_id="PET.RWTC.D",
        start_date="2025-01-01",
        end_date="2026-09-22",
    )

    print("API request successful.")

    records = data["response"]["data"]

    print(f"Records received: {len(records)}")

    print("\nFirst record:")
    print(records[0])