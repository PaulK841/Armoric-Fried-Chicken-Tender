"""
Sentiment Analysis Module for Campaign Feedback.
Uses TextBlob for sentiment classification of feedback comments.
"""

from textblob import TextBlob


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of a text comment.

    Returns:
        dict with keys: label (positive/neutral/negative), score (float -1 to 1)
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {"label": label, "score": round(polarity, 4)}


def batch_analyze(comments: list[str]) -> list[dict]:
    """Analyze sentiment for a list of comments."""
    return [analyze_sentiment(c) for c in comments]


if __name__ == "__main__":
    # Demo with sample comments
    test_comments = [
        "Great campaign!",
        "Not very engaging.",
        "Loved the product presentation.",
        "Too many details, hard to follow.",
        "Clear and concise message.",
        "Could be better organized.",
        "Excellent marketing strategy.",
        "Creative and fun approach!",
    ]

    print("Sentiment Analysis Results")
    print("=" * 50)
    for comment in test_comments:
        result = analyze_sentiment(comment)
        print(f"  '{comment}'")
        print(f"    -> {result['label']} (score: {result['score']})")
        print()
