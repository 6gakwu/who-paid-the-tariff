"""Work out how much of each product Canada imported from the US, in two periods:

- 2024: the last full year before any tariffs
- Tariff-free window: Sep 2025 - Aug 2026, between the end of the 2025 tariffs and the start of the 2026 ones

Saves two files to data/processed/:
- us_import_shares_2024.csv
- us_imports_by_period.csv
"""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FILE_2024 = PROCESSED_DIR / "us_import_shares_2024.csv"
FILE_BY_PERIOD = PROCESSED_DIR / "us_imports_by_period.csv"


def read_imports(year):
    """Read one year's import file (6-digit HS codes, by country), keeping only the columns we need."""
    file = next((RAW_DIR / f"imports_{year}").rglob("ODPFN015_*.csv"))
    imports = pd.read_csv(
        file,
        usecols=["YearMonth/AnnéeMois", "HS6", "Country/Pays", "Value/Valeur"],
        dtype={"YearMonth/AnnéeMois": str, "HS6": str, "Country/Pays": str},
    )
    return imports.rename(columns={
        "YearMonth/AnnéeMois": "month",
        "HS6": "hs6_code",
        "Country/Pays": "country",
        "Value/Valeur": "value",
    })


def import_totals(imports):
    """Total imports, imports from the US, and the US share, for each 6-digit code."""
    total_imports = imports.groupby("hs6_code")["value"].sum()
    us_imports = imports[imports["country"] == "US"].groupby("hs6_code")["value"].sum()

    totals = pd.DataFrame({"total_imports_cad": total_imports, "us_imports_cad": us_imports})
    totals["us_imports_cad"] = totals["us_imports_cad"].fillna(0)   # codes with no US imports
    totals["us_share"] = totals["us_imports_cad"] / totals["total_imports_cad"]
    return totals


def build_us_imports():
    # Period 1: all of 2024
    totals_2024 = import_totals(read_imports(2024))

    # Period 2: tariff-free window, Sep-Dec from the 2025 file plus Jan-Aug from the 2026 file
    imports_2025_2026 = pd.concat([read_imports(2025), read_imports(2026)])
    in_window = imports_2025_2026["month"].between("202509", "202608")
    imports_tariff_free = imports_2025_2026[in_window]
    print("Months in tariff-free window:", imports_tariff_free["month"].nunique())   # should be 12
    totals_tariff_free = import_totals(imports_tariff_free)

    # File 1: 2024 only, same format as before
    totals_2024.to_csv(FILE_2024)
    print(f"Saved {FILE_2024.name}: {len(totals_2024)} product codes")

    # File 2: both periods side by side, one row per product code
    by_period = totals_2024.add_suffix("_2024").join(
        totals_tariff_free.add_suffix("_tariff_free"), how="outer"
    )
    by_period.to_csv(FILE_BY_PERIOD)
    print(f"Saved {FILE_BY_PERIOD.name}: {len(by_period)} product codes")


if __name__ == "__main__":
    build_us_imports()