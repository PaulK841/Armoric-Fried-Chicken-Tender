"""
Armoric Fried Chicken Tender - Analytics Dashboard.
Streamlit application for visualizing sales and campaign feedback data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.connection import get_session
from ml.campaign_analysis import (
    get_sales_summary,
    get_feedback_summary,
    campaign_performance,
    sales_by_product,
    sales_by_country,
    monthly_sales_trend,
)

st.set_page_config(
    page_title="Armoric Fried Chicken Tender - Analytics",
    page_icon="🍗",
    layout="wide",
)

st.title("Armoric Fried Chicken Tender")
st.subheader("Campaign & Sales Analytics Dashboard")


@st.cache_data(ttl=60)
def load_data():
    session = get_session()
    try:
        sales_df = get_sales_summary(session)
        feedback_df = get_feedback_summary(session)
        perf_df = campaign_performance(session)
        product_df = sales_by_product(session)
        country_df = sales_by_country(session)
        trend_df = monthly_sales_trend(session)
    finally:
        session.close()
    return sales_df, feedback_df, perf_df, product_df, country_df, trend_df


sales_df, feedback_df, perf_df, product_df, country_df, trend_df = load_data()

if sales_df.empty and feedback_df.empty:
    st.error("No data found in the database. Please run the ETL pipelines first:")
    st.code("python pipelines/etl_sales.py\npython pipelines/etl_feedback.py")
    st.stop()

# --- KPI Metrics ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

if not sales_df.empty:
    col1.metric("Total Revenue", f"${sales_df['total_amount'].sum():,.2f}")
    col2.metric("Total Transactions", f"{len(sales_df):,}")
    col3.metric("Countries", f"{sales_df['country'].nunique()}")
    col4.metric("Products", f"{sales_df['product'].nunique()}")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Sales Analysis", "Campaign Feedback", "Campaign Impact"])

# ============ TAB 1: Sales Analysis ============
with tab1:
    st.header("Sales Overview")

    if not sales_df.empty:
        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_countries = st.multiselect(
                "Filter by Country", options=sorted(sales_df["country"].unique()), default=[]
            )
        with col_f2:
            selected_products = st.multiselect(
                "Filter by Product", options=sorted(sales_df["product"].unique()), default=[]
            )

        filtered_sales = sales_df.copy()
        if selected_countries:
            filtered_sales = filtered_sales[filtered_sales["country"].isin(selected_countries)]
        if selected_products:
            filtered_sales = filtered_sales[filtered_sales["product"].isin(selected_products)]

        # Monthly trend
        if not trend_df.empty:
            st.subheader("Monthly Revenue Trend")
            fig_trend = px.bar(
                trend_df, x="month", y="total_revenue",
                title="Monthly Revenue",
                labels={"month": "Month", "total_revenue": "Revenue ($)"},
                color_discrete_sequence=["#2E86AB"],
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        col_a, col_b = st.columns(2)

        # Sales by product
        with col_a:
            if not product_df.empty:
                st.subheader("Revenue by Product")
                fig_prod = px.pie(
                    product_df, values="total_revenue", names="product",
                    title="Revenue Distribution by Product",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                st.plotly_chart(fig_prod, use_container_width=True)

        # Sales by country
        with col_b:
            if not country_df.empty:
                st.subheader("Revenue by Country")
                fig_country = px.bar(
                    country_df, x="country", y="total_revenue",
                    title="Revenue by Country",
                    labels={"country": "Country", "total_revenue": "Revenue ($)"},
                    color="country",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                st.plotly_chart(fig_country, use_container_width=True)

        # Data table
        st.subheader("Sales Data")
        st.dataframe(filtered_sales, use_container_width=True, height=300)
    else:
        st.warning("No sales data available.")

# ============ TAB 2: Campaign Feedback ============
with tab2:
    st.header("Campaign Feedback Analysis")

    if not feedback_df.empty:
        col_s1, col_s2, col_s3 = st.columns(3)
        sentiment_counts = feedback_df["sentiment"].value_counts()
        col_s1.metric("Positive", sentiment_counts.get("positive", 0))
        col_s2.metric("Neutral", sentiment_counts.get("neutral", 0))
        col_s3.metric("Negative", sentiment_counts.get("negative", 0))

        col_c, col_d = st.columns(2)

        with col_c:
            st.subheader("Sentiment Distribution")
            fig_sent = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Feedback Sentiment Distribution",
                color=sentiment_counts.index,
                color_discrete_map={"positive": "#2ecc71", "neutral": "#f39c12", "negative": "#e74c3c"},
            )
            st.plotly_chart(fig_sent, use_container_width=True)

        with col_d:
            st.subheader("Sentiment Score Distribution")
            fig_hist = px.histogram(
                feedback_df, x="sentiment_score", nbins=20,
                title="Sentiment Score Histogram",
                labels={"sentiment_score": "Sentiment Score"},
                color_discrete_sequence=["#3498db"],
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Latest comments
        st.subheader("Latest Comments")
        latest_fb = feedback_df.sort_values("feedback_date", ascending=False).head(10)
        st.dataframe(
            latest_fb[["feedback_date", "username", "campaign_id", "comment", "sentiment", "sentiment_score"]],
            use_container_width=True,
            height=300,
            column_config={
                "feedback_date": "Date",
                "username": "User",
                "campaign_id": "Campaign",
                "comment": "Comment",
                "sentiment": "Sentiment",
                "sentiment_score": st.column_config.NumberColumn("Score", format="%.2f"),
            },
        )

        # Full feedback table
        st.subheader("All Feedback Data")
        st.dataframe(feedback_df, use_container_width=True, height=300)
    else:
        st.warning("No feedback data available.")

# ============ TAB 3: Campaign Impact ============
with tab3:
    st.header("Campaign Impact on Sales")

    if not perf_df.empty:
        st.subheader("Campaign Performance")
        fig_perf = px.bar(
            perf_df.head(20),
            x="campaign_id", y="avg_sentiment_score",
            color="feedback_count",
            title="Campaign Sentiment Scores (Top 20)",
            labels={
                "campaign_id": "Campaign",
                "avg_sentiment_score": "Avg Sentiment Score",
                "feedback_count": "# Feedbacks",
            },
            color_continuous_scale="RdYlGn",
        )
        fig_perf.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_perf, use_container_width=True)

        st.subheader("Campaign Details")
        st.dataframe(perf_df, use_container_width=True, height=300)
    else:
        st.warning("No campaign performance data available.")

st.markdown("---")
st.caption("Armoric Fried Chicken Tender - Data Engineering Project 2025")
