"""
Airflow DAG for Armoric Fried Chicken Tender - Sales ETL Pipeline.
Orchestrates the batch ingestion and transformation of sales data.
Feedback data is handled in real-time via the FastAPI REST API.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "armoric",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "armoric_sales_pipeline",
    default_args=default_args,
    description="Batch ETL pipeline for sales data - extracts CSV, transforms, and loads into database",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["armoric", "etl", "sales", "batch"],
)


def run_sales_etl():
    """Execute the sales ETL pipeline."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from pipelines.etl_sales import run
    run()


def run_sales_analysis():
    """Execute sales analysis (by product, country, monthly trend)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ml.campaign_analysis import sales_by_product, sales_by_country, monthly_sales_trend
    from database.connection import get_session

    session = get_session()
    try:
        products = sales_by_product(session)
        countries = sales_by_country(session)
        trend = monthly_sales_trend(session)
        print(f"Sales analysis completed: {len(products)} products, {len(countries)} countries, {len(trend)} months")
    finally:
        session.close()


# Task definitions
task_sales_etl = PythonOperator(
    task_id="etl_sales",
    python_callable=run_sales_etl,
    dag=dag,
)

task_sales_analysis = PythonOperator(
    task_id="sales_analysis",
    python_callable=run_sales_analysis,
    dag=dag,
)

# Pipeline: ETL sales → then analysis
task_sales_etl >> task_sales_analysis
