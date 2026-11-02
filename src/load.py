"""Load the crosswalk and cleaned prices into PostgreSQL. Run sql/schema.sql first."""
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CROSSWALK_FILE = PROJECT_ROOT / "data" / "reference" / "product_tariff_crosswalk.csv"
PRICES_FILE = PROJECT_ROOT / "data" / "processed" / "prices_clean.csv"


def load_all():
    crosswalk = pd.read_csv(CROSSWALK_FILE, dtype=str)[["product", "status", "hs_code"]]
    prices = pd.read_csv(PRICES_FILE, parse_dates=["date"])[["date", "place", "product", "price"]]

    engine = get_engine()
    with engine.begin() as connection:
        # Empty both tables so the script can be rerun without duplicating rows
        connection.execute(text("TRUNCATE prices, product_tariff_crosswalk"))

        # Crosswalk first: prices.product must refer to an existing crosswalk row
        crosswalk.to_sql("product_tariff_crosswalk", connection, if_exists="append", index=False)
        prices.to_sql("prices", connection, if_exists="append", index=False, chunksize=10_000)

    print(f"Loaded {len(crosswalk)} crosswalk rows and {len(prices)} price rows")


if __name__ == "__main__":
    load_all()