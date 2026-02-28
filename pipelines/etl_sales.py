"""
ETL Pipeline for Sales Data.
Extracts data from sales_data.csv, transforms it, and loads it into the database.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SALES_DATA_PATH
from database.connection import engine
from database.models import Base, Sale, Campaign
from pipelines.transformations import clean_sales_data
from database.connection import get_session


def extract(filepath: Path) -> pd.DataFrame:
    """Extract: read sales CSV file."""
    print(f"[Extract] Reading sales data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"[Extract] Loaded {len(df)} records.")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform: clean and validate sales data."""
    print("[Transform] Cleaning sales data...")
    df = clean_sales_data(df)
    print(f"[Transform] {len(df)} records after cleaning.")
    return df


def load(df: pd.DataFrame):
    """Load: insert sales data into database."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    session = get_session()
    try:
        # Clear existing sales data to avoid duplicates on re-run
        session.query(Sale).delete()
        session.commit()

        # Insert records
        records = []
        for _, row in df.iterrows():
            sale = Sale(
                username=row["username"],
                sale_date=row["sale_date"],
                country=row["country"],
                product=row["product"],
                quantity=int(row["quantity"]),
                unit_price=float(row["unit_price"]),
                total_amount=float(row["total_amount"]),
            )
            records.append(sale)

        session.bulk_save_objects(records)
        session.commit()
        print(f"[Load] Inserted {len(records)} sales records into database.")
    except Exception as e:
        session.rollback()
        print(f"[Load] Error: {e}")
        raise
    finally:
        session.close()


def run():
    """Run the complete ETL pipeline for sales data."""
    print("=" * 50)
    print("Sales ETL Pipeline")
    print("=" * 50)

    df = extract(SALES_DATA_PATH)
    df = transform(df)
    load(df)

    print("[Done] Sales ETL pipeline completed successfully.")


if __name__ == "__main__":
    run()
