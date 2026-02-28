-- Armoric Fried Chicken Tender - Database Schema
-- SQLite compatible

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    name TEXT,
    start_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    sale_date DATE NOT NULL,
    country TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_amount REAL NOT NULL,
    campaign_id TEXT,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    feedback_date DATE NOT NULL,
    campaign_id TEXT NOT NULL,
    comment TEXT NOT NULL,
    sentiment TEXT,
    sentiment_score REAL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_country ON sales(country);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product);
CREATE INDEX IF NOT EXISTS idx_feedback_campaign ON feedback(campaign_id);
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment);
