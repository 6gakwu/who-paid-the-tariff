"""Script to convert Canada's counter-tariff lists (HS codes, descriptions, rates) into CSV files.

canada.ca blocks scripted downloads, so each list page is saved manually from a
browser into data/reference/tariff_pages/ (committed to the repo). This script
reads those saved pages and writes one CSV per list to data/raw/tariffs/.
"""
from io import StringIO
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "data" / "reference" / "tariff_pages"   # saved pages (in)
OUT_DIR = ROOT / "data" / "raw" / "tariffs"  

# File name -> the page it was saved from for reproducibility
LISTS = {
    "counter_tariffs_2025_03": "https://www.canada.ca/en/department-finance/news/2025/03/list-of-products-from-the-united-states-subject-to-25-per-cent-tariffs-effective-march-4-2025.html",
    "counter_tariffs_2026_09": "https://www.canada.ca/en/department-finance/news/2026/08/list-of-products-from-the-united-states-subject-to-counter-tariffs-effective-september-8-2026.html",
}

def convert_tariff_list(name: str, url: str) -> Path:
    """Read one saved tariff page and save all its tables as a single CSV."""
    page_path = PAGES_DIR / f"{name}.html"
    if not page_path.exists():
        raise SystemExit(
            f"\nMissing {page_path.name}.\n"
            f"Open {url}\n"
            f"press Ctrl+S, choose 'Webpage, HTML Only', and save it as:\n  {page_path}"
        )

    print(f"Reading {page_path.name} ...")
    html = page_path.read_text(encoding="utf-8", errors="replace")

    tables = pd.read_html(StringIO(html))           # every table on the page
    combined = pd.concat(tables, ignore_index=True)

    # Clean column names
    combined.columns = [c.replace("\xa0", " ").strip().lower() for c in combined.columns]
    combined = combined.rename(columns={
        "tariff item": "tariff_item",
        "harmonized system (hs) heading": "hs_heading",
        "indicative description": "description",
        "tariff rate": "rate",
    })

    out_path = OUT_DIR / f"{name}.csv"
    combined.to_csv(out_path, index=False)
    print(f"  {len(tables)} table(s), {len(combined)} rows -> {out_path.name}")
    return out_path

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in LISTS.items():
        convert_tariff_list(name, url)