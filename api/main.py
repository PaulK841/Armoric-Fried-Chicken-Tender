"""
Armoric Fried Chicken Tender - Campaign Feedback REST API.
FastAPI application for managing campaign feedback and sales data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db, engine
from database.models import Base
from api.schemas import FeedbackCreate, FeedbackResponse, CampaignResponse, SaleResponse
from api.crud import create_feedback, get_feedbacks, get_feedback_by_id, get_campaigns, get_sales

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Armoric Fried Chicken Tender API",
    description="REST API for campaign feedback management and sales data analysis",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Armoric Fried Chicken Tender API"}


# --- Feedback Endpoints ---

@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit new campaign feedback. Sentiment is automatically analyzed."""
    return create_feedback(
        db=db,
        username=feedback.username,
        campaign_id=feedback.campaign_id,
        comment=feedback.comment,
        feedback_date=feedback.feedback_date,
    )


@app.get("/feedback", response_model=list[FeedbackResponse])
def list_feedback(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all feedback entries with optional filters."""
    return get_feedbacks(db, campaign_id=campaign_id, skip=skip, limit=limit)


@app.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
def get_single_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """Get a single feedback entry by ID."""
    fb = get_feedback_by_id(db, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return fb


# --- Campaign Endpoints ---

@app.get("/campaigns", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns."""
    return get_campaigns(db)


# --- Sales Endpoints ---

@app.get("/sales", response_model=list[SaleResponse])
def list_sales(
    country: Optional[str] = Query(None, description="Filter by country"),
    product: Optional[str] = Query(None, description="Filter by product"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List sales data with optional filters."""
    return get_sales(db, country=country, product=product, skip=skip, limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
