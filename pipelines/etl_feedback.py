"""
ETL Pipeline for Feedback Data.
Extracts data from feedback_data.json, transforms it (with sentiment analysis), and loads it into the database.
"""

import sys
from pathlib import Path
import json
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import FEEDBACK_DATA_PATH
from database.connection import engine, get_session
from database.models import Base, Feedback, Campaign
from pipelines.transformations import clean_feedback_data, enrich_feedback_with_sentiment


def extract(filepath: Path) -> pd.DataFrame:
    """Extract: read feedback JSON file."""
    print(f"[Extract] Reading feedback data from {filepath}...")
    with open(filepath, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"[Extract] Loaded {len(df)} records.")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform: clean feedback data and add sentiment analysis."""
    print("[Transform] Cleaning feedback data...")
    df = clean_feedback_data(df)
    print(f"[Transform] {len(df)} records after cleaning.")

    print("[Transform] Running sentiment analysis...")
    df = enrich_feedback_with_sentiment(df)
    sentiment_counts = df["sentiment"].value_counts().to_dict()
    print(f"[Transform] Sentiment distribution: {sentiment_counts}")
    return df


def load(df: pd.DataFrame):
    """Load: insert feedback data and campaigns into database."""
    Base.metadata.create_all(bind=engine)

    session = get_session()
    try:
        # Insert unique campaigns
        existing_campaigns = {c.campaign_id for c in session.query(Campaign).all()}
        unique_campaigns = df["campaign_id"].unique()
        new_campaigns = [
            Campaign(campaign_id=cid)
            for cid in unique_campaigns
            if cid not in existing_campaigns
        ]
        if new_campaigns:
            session.bulk_save_objects(new_campaigns)
            session.commit()
            print(f"[Load] Inserted {len(new_campaigns)} new campaigns.")

        # Clear existing feedback to avoid duplicates on re-run
        session.query(Feedback).delete()
        session.commit()

        # Insert feedback records
        records = []
        for _, row in df.iterrows():
            fb = Feedback(
                username=row["username"],
                feedback_date=row["feedback_date"],
                campaign_id=row["campaign_id"],
                comment=row["comment"],
                sentiment=row["sentiment"],
                sentiment_score=float(row["sentiment_score"]),
            )
            records.append(fb)

        session.bulk_save_objects(records)
        session.commit()
        print(f"[Load] Inserted {len(records)} feedback records into database.")
    except Exception as e:
        session.rollback()
        print(f"[Load] Error: {e}")
        raise
    finally:
        session.close()


def run():
    """Run the complete ETL pipeline for feedback data."""
    print("=" * 50)
    print("Feedback ETL Pipeline")
    print("=" * 50)

    df = extract(FEEDBACK_DATA_PATH)
    df = transform(df)
    load(df)

    print("[Done] Feedback ETL pipeline completed successfully.")


if __name__ == "__main__":
    run()
