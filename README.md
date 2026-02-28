# Armoric Fried Chicken Tender - Data Engineering Project

## Overview

This project implements a complete data engineering solution for **Armoric Fried Chicken Tender**, covering campaign feedback management, sales data processing, AI/ML sentiment analysis, and analytics dashboards.

## Architecture

```
Sales Part:     Airflow DAG → Python ELT → SQLite Database → Streamlit Dashboard
Feedback Part:  User → FastAPI REST API → Sentiment Analysis → SQLite Database
```

## Project Structure

```
Final_Project/
├── api/                    # FastAPI REST API
│   ├── main.py             # API application & endpoints
│   ├── schemas.py          # Pydantic request/response models
│   └── crud.py             # Database CRUD operations
├── database/               # Database layer
│   ├── init.sql            # SQL schema creation script
│   ├── models.py           # SQLAlchemy ORM models
│   └── connection.py       # Database connection utility
├── pipelines/              # Data processing pipelines
│   ├── etl_sales.py        # Sales data ETL pipeline
│   ├── etl_feedback.py     # Feedback data ETL pipeline
│   └── transformations.py  # Data cleaning & transformation functions
├── dags/                   # Airflow DAGs
│   └── etl_dag.py          # ETL orchestration DAG
├── ml/                     # AI/ML modules
│   ├── sentiment.py        # Sentiment analysis (TextBlob)
│   └── campaign_analysis.py# Campaign impact analysis
├── dashboard/              # Analytics dashboard
│   └── app.py              # Streamlit dashboard application
├── data/                   # SQLite database (auto-created)
├── config.py               # Central configuration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose orchestration
├── sales_data.csv          # Source sales data (1000 records)
└── feedback_data.json      # Source feedback data (100 records)
```

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

## Usage

### 1. Run ETL Pipelines (Load Data)

```bash
# Load sales data into database
python pipelines/etl_sales.py

# Load feedback data with sentiment analysis
python pipelines/etl_feedback.py
```

### 2. Start the REST API

```bash
uvicorn api.main:app --reload
```

API documentation available at: http://localhost:8000/docs

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/feedback` | Submit new feedback (auto sentiment analysis) |
| GET | `/feedback` | List feedback (filter by campaign_id) |
| GET | `/feedback/{id}` | Get single feedback |
| GET | `/campaigns` | List all campaigns |
| GET | `/sales` | List sales (filter by country, product) |

### 3. Launch Analytics Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard available at: http://localhost:8501

### 4. Run Sentiment Analysis Standalone

```bash
python ml/sentiment.py
```

### 5. Run Campaign Analysis

```bash
python ml/campaign_analysis.py
```

## Docker Deployment

```bash
docker-compose up --build
```

Services:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- Airflow: http://localhost:8080

## Database Schema

### Tables

- **campaigns**: campaign_id (PK), name, start_date, end_date
- **sales**: id (PK), username, sale_date, country, product, quantity, unit_price, total_amount, campaign_id (FK)
- **feedback**: id (PK), username, feedback_date, campaign_id (FK), comment, sentiment, sentiment_score

## Data Processing Pipeline

1. **Extract**: Read raw data from CSV (sales) and JSON (feedback)
2. **Transform**: Clean, validate, remove duplicates, enrich with sentiment analysis
3. **Load**: Insert processed data into SQLite database

## AI/ML Model

- **Sentiment Analysis**: Uses TextBlob NLP to classify feedback comments as positive, neutral, or negative
- **Campaign Analysis**: Aggregates campaign performance metrics, correlates feedback sentiment with sales data

## Analytics Dashboard

The Streamlit dashboard provides:
- **Sales Analysis**: Revenue trends, product distribution, country breakdown
- **Campaign Feedback**: Sentiment distribution, score histograms
- **Campaign Impact**: Campaign performance rankings, sentiment scores

## Technologies

- **API**: FastAPI, Uvicorn, Pydantic
- **Database**: SQLite, SQLAlchemy ORM
- **ETL**: Pandas, Python
- **ML/NLP**: TextBlob
- **Dashboard**: Streamlit, Plotly
- **Orchestration**: Apache Airflow
- **Containerization**: Docker, Docker Compose
