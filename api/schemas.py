"""Pydantic schemas for the FastAPI application."""

from pydantic import BaseModel
from datetime import date
from typing import Optional


# --- Feedback ---

class FeedbackCreate(BaseModel):
    username: str
    campaign_id: str
    comment: str
    feedback_date: Optional[date] = None


class FeedbackResponse(BaseModel):
    id: int
    username: str
    feedback_date: date
    campaign_id: str
    comment: str
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

    class Config:
        from_attributes = True


# --- Campaign ---

class CampaignResponse(BaseModel):
    campaign_id: str
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        from_attributes = True


# --- Sales ---

class SaleResponse(BaseModel):
    id: int
    username: str
    sale_date: date
    country: str
    product: str
    quantity: int
    unit_price: float
    total_amount: float
    campaign_id: Optional[str] = None

    class Config:
        from_attributes = True
