# ==================================================
# Sentiment Analysis for Mumbai Local Train Reviews
# ==================================================
# Uses VADER (Valence Aware Dictionary and sEntiment Reasoner)
# Lightweight, no model downloads, works on social media text
# ==================================================

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None and VADER_AVAILABLE:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def analyze_sentiment(text):
    """
    Analyze sentiment of a single review text.
    Returns dict with label, score, emoji, color.
    """
    analyzer = _get_analyzer()
    if analyzer is None or not text or not text.strip():
        return {
            "label": "Neutral",
            "score": 0.0,
            "emoji": "~",
            "color": "#94a3b8"
        }

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        return {
            "label": "Positive",
            "score": compound,
            "emoji": "+",
            "color": "#4ade80"
        }
    elif compound <= -0.05:
        return {
            "label": "Negative",
            "score": compound,
            "emoji": "-",
            "color": "#f87171"
        }
    else:
        return {
            "label": "Neutral",
            "score": compound,
            "emoji": "~",
            "color": "#fbbf24"
        }


def analyze_reviews_batch(reviews):
    """Add sentiment data to a list of review dicts."""
    for review in reviews:
        comment = review.get("comment", "")
        review["sentiment"] = analyze_sentiment(comment)
    return reviews


def get_sentiment_summary(reviews):
    """Compute overall sentiment summary for a collection of reviews."""
    if not reviews:
        return {
            "total": 0, "positive": 0, "neutral": 0, "negative": 0,
            "avg_score": 0.0, "overall_label": "No reviews", "overall_emoji": "—"
        }

    for r in reviews:
        if "sentiment" not in r:
            r["sentiment"] = analyze_sentiment(r.get("comment", ""))

    total = len(reviews)
    positive = sum(1 for r in reviews if r["sentiment"]["label"] == "Positive")
    neutral = sum(1 for r in reviews if r["sentiment"]["label"] == "Neutral")
    negative = sum(1 for r in reviews if r["sentiment"]["label"] == "Negative")
    avg_score = sum(r["sentiment"]["score"] for r in reviews) / total

    if avg_score >= 0.05:
        overall_label, overall_emoji = "Mostly Positive", "+"
    elif avg_score <= -0.05:
        overall_label, overall_emoji = "Mostly Negative", "-"
    else:
        overall_label, overall_emoji = "Mixed", "~"

    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "avg_score": round(avg_score, 3),
        "overall_label": overall_label,
        "overall_emoji": overall_emoji
    }


def format_sentiment_bar(summary):
    """Generate HTML sentiment bar for Streamlit display."""
    total = summary["total"]
    if total == 0:
        return ""

    pos_pct = (summary["positive"] / total) * 100
    neu_pct = (summary["neutral"] / total) * 100
    neg_pct = (summary["negative"] / total) * 100

    return f"""
    <div style="margin: 8px 0;">
        <small style="color: #94a3b8;">Sentiment: {summary['overall_label']}</small>
        <div style="display:flex; height:6px; border-radius:3px; overflow:hidden; margin-top:4px;">
            <div style="width:{pos_pct}%; background:#4ade80;"></div>
            <div style="width:{neu_pct}%; background:#fbbf24;"></div>
            <div style="width:{neg_pct}%; background:#f87171;"></div>
        </div>
        <small style="color:#64748b; font-size:0.7rem;">
            {summary['positive']} positive / {summary['neutral']} neutral / {summary['negative']} negative
        </small>
    </div>
    """
