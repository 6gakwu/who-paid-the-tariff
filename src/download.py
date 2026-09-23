"""Download raw StatCan tables into data/raw/."""
from pathlib import Path
import io
import zipfile

import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

TABLES = {
    "retail_prices": "18100245",   # Monthly average retail prices
    "cpi": "18100004",             # Consumer Price Index
}


def download_table(table_id: str, name: str) -> Path:
    """Download one StatCan table as a zip and unzip it into data/raw/<name>/."""
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"
    print(f"Downloading {name} from {url} ...")
    response = requests.get(url, timeout=300)
    response.raise_for_status()

    out_folder = RAW_DIR / name
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(out_folder)
    return out_folder


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, table_id in TABLES.items():
        folder = download_table(table_id, name)
        print(f"Saved to {folder}")