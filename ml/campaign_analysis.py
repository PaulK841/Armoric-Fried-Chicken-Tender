"""
Campaign Impact Analysis Module.
Analyzes the relationship between marketing campaigns, feedback sentiment, and sales performance.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_session
from database.models import Sale, Feedback, Campaign


def get_sales_summary(session) -> pd.DataFrame:
    """Get sales summary aggregated by product and country."""
    sales = session.query(Sale).all()
    df = pd.DataFrame([{
        "username": s.username,
        "sale_date": s.sale_date,
        "country": s.country,
        "product": s.product,
        "quantity": s.quantity,
        "unit_price": s.unit_price,
        "total_amount": s.total_amount,
        "campaign_id": s.campaign_id,
    } for s in sales])
    return df


def get_feedback_summary(session) -> pd.DataFrame:
    """Get feedback summary with sentiment data."""
    feedbacks = session.query(Feedback).all()
    df = pd.DataFrame([{
        "username": f.username,
        "feedback_date": f.feedback_date,
        "campaign_id": f.campaign_id,
        "comment": f.comment,
        "sentiment": f.sentiment,
        "sentiment_score": f.sentiment_score,
    } for f in feedbacks])
    return df


def campaign_performance(session) -> pd.DataFrame:
    """
    Compute campaign performance metrics:
    - Number of feedbacks per campaign
    - Average sentiment score
    - Sentiment distribution
    """
    df = get_feedback_summary(session)
    if df.empty:
        return pd.DataFrame()

    stats = df.groupby("campaign_id").agg(
        feedback_count=("comment", "count"),
        avg_sentiment_score=("sentiment_score", "mean"),
        positive_count=("sentiment", lambda x: (x == "positive").sum()),
        neutral_count=("sentiment", lambda x: (x == "neutral").sum()),
        negative_count=("sentiment", lambda x: (x == "negative").sum()),
    ).reset_index()

    stats["avg_sentiment_score"] = stats["avg_sentiment_score"].round(4)
    return stats.sort_values("avg_sentiment_score", ascending=False)


def sales_by_product(session) -> pd.DataFrame:
    """Aggregate sales by product."""
    df = get_sales_summary(session)
    if df.empty:
        return pd.DataFrame()

    return df.groupby("product").agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("total_amount", "sum"),
        avg_price=("unit_price", "mean"),
        num_transactions=("username", "count"),
    ).reset_index().sort_values("total_revenue", ascending=False)


def sales_by_country(session) -> pd.DataFrame:
    """Aggregate sales by country."""
    df = get_sales_summary(session)
    if df.empty:
        return pd.DataFrame()

    return df.groupby("country").agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("total_amount", "sum"),
        num_transactions=("username", "count"),
    ).reset_index().sort_values("total_revenue", ascending=False)


def monthly_sales_trend(session) -> pd.DataFrame:
    """Compute monthly sales trend."""
    df = get_sales_summary(session)
    if df.empty:
        return pd.DataFrame()

    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["month"] = df["sale_date"].dt.to_period("M").astype(str)

    return df.groupby("month").agg(
        total_revenue=("total_amount", "sum"),
        total_quantity=("quantity", "sum"),
        num_transactions=("username", "count"),
    ).reset_index()


if __name__ == "__main__":
    session = get_session()
    try:
        print("=== Campaign Performance ===")
        perf = campaign_performance(session)
        if not perf.empty:
            print(perf.to_string(index=False))
        else:
            print("No feedback data. Run ETL pipelines first.")

        print("\n=== Sales by Product ===")
        products = sales_by_product(session)
        if not products.empty:
            print(products.to_string(index=False))
        else:
            print("No sales data. Run ETL pipelines first.")

        print("\n=== Sales by Country ===")
        countries = sales_by_country(session)
        if not countries.empty:
            print(countries.to_string(index=False))

        print("\n=== Monthly Sales Trend ===")
        trend = monthly_sales_trend(session)
        if not trend.empty:
            print(trend.to_string(index=False))
    finally:
        session.close()
