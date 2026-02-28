from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    feedbacks = relationship("Feedback", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(campaign_id={self.campaign_id})>"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    sale_date = Column(Date, nullable=False)
    country = Column(String, nullable=False)
    product = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"), nullable=True)

    def __repr__(self):
        return f"<Sale(id={self.id}, product={self.product}, total={self.total_amount})>"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    feedback_date = Column(Date, nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"), nullable=False)
    comment = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    sentiment_score = Column(Float, nullable=True)

    campaign = relationship("Campaign", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, sentiment={self.sentiment})>"
