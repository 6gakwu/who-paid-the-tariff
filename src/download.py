"""Download raw StatCan data into data/raw/. """
from pathlib import Path
import io
import zipfile

import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# StatCan tables, by table number
TABLES = {
    "retail_prices": "18100245",   # monthly average retail prices
    "cpi": "18100004",             # Consumer Price Index
}

# Other StatCan files, by direct address
OTHER_FILES = {
    # All Canadian imports in 2024, by product code and country (last full year before the tariffs)
    "imports_2024": "https://www150.statcan.gc.ca/n1/pub/71-607-x/2021004/zip/CIMT-CICM_Imp_2024.zip",
}


def table_url(table_id):
    """Download address for a StatCan table."""
    return f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"


def download_zip(url, name):
    """Download a zip file and unzip it into data/raw/<name>/, unless that folder already exists."""
    out_folder = RAW_DIR / name
    if out_folder.exists():
        print(f"Skipping {name}: already downloaded")
        return out_folder

    print(f"Downloading {name} ...")
    response = requests.get(url, timeout=600)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(out_folder)
    print(f"Saved to {out_folder}")
    return out_folder


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for name, table_id in TABLES.items():
        download_zip(table_url(table_id), name)

    for name, url in OTHER_FILES.items():
        download_zip(url, name)