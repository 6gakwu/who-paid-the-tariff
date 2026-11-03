"""Work out how much of each product Canada imported from the US in 2024.

Reads StatCan's 2024 import file (6-digit HS codes, by country) and saves, for every code,
total imports, imports from the US, and the US share, to data/processed/us_import_shares_2024.csv.
"""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMPORTS_FILE = PROJECT_ROOT / "data" / "raw" / "imports_2024" / "CIMT-CICM_Imp_2024" / "ODPFN015_202412N.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "us_import_shares_2024.csv"


def build_us_import_shares():
    # Read only the 3 columns we need, and give them simple names
    imports = pd.read_csv(
        IMPORTS_FILE,
        usecols=["HS6", "Country/Pays", "Value/Valeur"],
        dtype={"HS6": str, "Country/Pays": str},
    )
    imports = imports.rename(columns={"HS6": "hs6_code", "Country/Pays": "country", "Value/Valeur": "value"})

    # Each code appears once per month, province and US state, so add everything up for the year
    total_imports = imports.groupby("hs6_code")["value"].sum()
    us_imports = imports[imports["country"] == "US"].groupby("hs6_code")["value"].sum()

    shares = pd.DataFrame({"total_imports_cad": total_imports, "us_imports_cad": us_imports})
    shares["us_imports_cad"] = shares["us_imports_cad"].fillna(0)     # codes with no US imports
    shares["us_share"] = shares["us_imports_cad"] / shares["total_imports_cad"]

    shares.to_csv(OUTPUT_FILE)
    print(f"Saved US import shares for {len(shares)} product codes")


if __name__ == "__main__":
    build_us_import_shares()