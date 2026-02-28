"""CRUD operations for the database."""

from datetime import date
from sqlalchemy.orm import Session
from database.models import Feedback, Campaign, Sale
from ml.sentiment import analyze_sentiment


def create_feedback(db: Session, username: str, campaign_id: str, comment: str, feedback_date: date = None) -> Feedback:
    """Create a new feedback entry with auto sentiment analysis."""
    if feedback_date is None:
        feedback_date = date.today()

    # Auto-analyze sentiment
    sentiment_result = analyze_sentiment(comment)

    # Ensure campaign exists
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        campaign = Campaign(campaign_id=campaign_id)
        db.add(campaign)
        db.flush()

    fb = Feedback(
        username=username,
        feedback_date=feedback_date,
        campaign_id=campaign_id,
        comment=comment,
        sentiment=sentiment_result["label"],
        sentiment_score=sentiment_result["score"],
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


def get_feedbacks(db: Session, campaign_id: str = None, skip: int = 0, limit: int = 100):
    """Get feedback entries with optional campaign filter."""
    query = db.query(Feedback)
    if campaign_id:
        query = query.filter(Feedback.campaign_id == campaign_id)
    return query.offset(skip).limit(limit).all()


def get_feedback_by_id(db: Session, feedback_id: int):
    """Get a single feedback by ID."""
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_campaigns(db: Session):
    """Get all campaigns."""
    return db.query(Campaign).all()


def get_sales(db: Session, country: str = None, product: str = None, skip: int = 0, limit: int = 100):
    """Get sales entries with optional filters."""
    query = db.query(Sale)
    if country:
        query = query.filter(Sale.country == country)
    if product:
        query = query.filter(Sale.product == product)
    return query.offset(skip).limit(limit).all()
