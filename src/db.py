"""Connect to the project's PostgreSQL database using the login details in .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")   # reads DB_USER, DB_PASSWORD, etc. into the environment


def get_engine():
    """Return a connection to the who_paid_the_tariff database."""
    url = (
        f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


if __name__ == "__main__":
    # Quick test: ask the database for its version
    with get_engine().connect() as connection:
        version = connection.execute(text("SELECT version()")).scalar()
    print("Connected:", version)