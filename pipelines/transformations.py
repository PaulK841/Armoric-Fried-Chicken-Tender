"""
Data transformation functions for the ETL pipeline.
Handles cleaning, validation, and enrichment of sales and feedback data.
"""

import pandas as pd
from datetime import datetime


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate sales data."""
    # Remove duplicates
    df = df.drop_duplicates()

    # Strip whitespace from string columns
    for col in ["username", "country", "product"]:
        df[col] = df[col].str.strip()

    # Parse dates
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date

    # Ensure numeric types
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0.0)

    # Remove rows with invalid data
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]

    return df.reset_index(drop=True)


def clean_feedback_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate feedback data."""
    # Remove duplicates
    df = df.drop_duplicates()

    # Strip whitespace
    for col in ["username", "campaign_id", "comment"]:
        df[col] = df[col].str.strip()

    # Parse dates
    df["feedback_date"] = pd.to_datetime(df["feedback_date"]).dt.date

    # Remove empty comments
    df = df[df["comment"].str.len() > 0]

    return df.reset_index(drop=True)


def enrich_feedback_with_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Add sentiment analysis to feedback data."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ml.sentiment import analyze_sentiment

    sentiments = df["comment"].apply(analyze_sentiment)
    df["sentiment"] = sentiments.apply(lambda x: x["label"])
    df["sentiment_score"] = sentiments.apply(lambda x: x["score"])
    return df
