# ==================================================
# Mumbai Local Train - Review System
# ==================================================
# 1. User-submitted reviews (stored in JSON)
# 2. Google Maps station reviews (scraped)
# 3. Twitter/X posts about trains (scraped)
# ==================================================

import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ---------------- FILE PATHS ----------------
BASE_DIR = os.path.dirname(__file__)
USER_REVIEWS_FILE = os.path.join(BASE_DIR, "user_reviews.json")
SCRAPED_REVIEWS_FILE = os.path.join(BASE_DIR, "scraped_reviews.json")


# ==================================================
# PART 1: USER REVIEWS SYSTEM
# ==================================================

def load_user_reviews():
    """Load user reviews from JSON file."""
    if os.path.exists(USER_REVIEWS_FILE):
        with open(USER_REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"reviews": []}


def save_user_reviews(data):
    """Save user reviews to JSON file."""
    with open(USER_REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_user_review(category, subject, rating, comment, username="Anonymous"):
    """Add a new user review."""
    data = load_user_reviews()

    review = {
        "id": len(data["reviews"]) + 1,
        "category": category,  # station, route, line, general
        "subject": subject,    # e.g., "Andheri Station", "Thane to CSMT"
        "rating": rating,      # 1-5
        "comment": comment,
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "source": "user"
    }

    data["reviews"].append(review)
    save_user_reviews(data)
    return review


def get_reviews_for(subject):
    """Get reviews for a specific station/route."""
    data = load_user_reviews()
    subject_lower = subject.lower()

    matching = []
    for review in data["reviews"]:
        if subject_lower in review["subject"].lower():
            matching.append(review)

    # Also check scraped reviews
    scraped = load_scraped_reviews()
    for review in scraped.get("reviews", []):
        if subject_lower in review.get("subject", "").lower():
            matching.append(review)

    return matching


def get_average_rating(subject):
    """Get average rating for a subject."""
    reviews = get_reviews_for(subject)
    if not reviews:
        return None

    ratings = [r["rating"] for r in reviews if r.get("rating")]
    if not ratings:
        return None

    return sum(ratings) / len(ratings)


# ==================================================
# PART 2: GOOGLE MAPS SCRAPING
# ==================================================

# Station coordinates for Google Maps
STATION_PLACES = {
    "Churchgate": "Churchgate Railway Station, Mumbai",
    "Dadar": "Dadar Railway Station, Mumbai",
    "Andheri": "Andheri Railway Station, Mumbai",
    "Borivali": "Borivali Railway Station, Mumbai",
    "Thane": "Thane Railway Station, Mumbai",
    "CSMT": "Chhatrapati Shivaji Terminus, Mumbai",
    "Kurla": "Kurla Railway Station, Mumbai",
    "Panvel": "Panvel Railway Station, Mumbai",
    "Vashi": "Vashi Railway Station, Mumbai",
    "Bandra": "Bandra Railway Station, Mumbai",
}


def scrape_google_maps_reviews(station_name):
    """
    Scrape reviews from Google Maps for a station.
    Note: Direct scraping is limited. For production, use Google Places API.
    """
    # Google Maps requires JavaScript, so we'll use a workaround
    # For now, return placeholder - in production use Google Places API

    print(f"[Google Maps] Would scrape reviews for: {station_name}")

    # Placeholder reviews based on common feedback patterns
    # In production, replace with actual API calls
    return []


# ==================================================
# PART 3: TWITTER/X SCRAPING
# ==================================================

def scrape_twitter_posts(query="Mumbai local train", limit=10):
    """
    Scrape Twitter posts about Mumbai local trains.
    Uses Nitter (Twitter frontend) as Twitter API requires paid access.
    """
    print(f"[Twitter] Searching for: {query}")

    # Try multiple Nitter instances
    nitter_instances = [
        "https://nitter.net",
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
    ]

    posts = []

    for nitter_url in nitter_instances:
        try:
            search_url = f"{nitter_url}/search?f=tweets&q={query.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.get(search_url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find tweet containers
                tweets = soup.find_all('div', class_='tweet-content')

                for tweet in tweets[:limit]:
                    text = tweet.get_text(strip=True)
                    if text:
                        posts.append({
                            "text": text,
                            "source": "twitter",
                            "timestamp": datetime.now().isoformat()
                        })

                if posts:
                    print(f"[Twitter] Found {len(posts)} posts from {nitter_url}")
                    break

        except Exception as e:
            print(f"[Twitter] Error with {nitter_url}: {e}")
            continue

    return posts


def scrape_railway_twitter():
    """Scrape official railway Twitter accounts."""
    accounts = [
        "WesternRly",      # Western Railway official
        "Central_Railway", # Central Railway official
    ]

    all_posts = []

    for account in accounts:
        try:
            nitter_url = f"https://nitter.net/{account}"
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(nitter_url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                tweets = soup.find_all('div', class_='tweet-content')

                for tweet in tweets[:5]:
                    text = tweet.get_text(strip=True)
                    if text:
                        all_posts.append({
                            "text": text,
                            "source": f"twitter/@{account}",
                            "account": account,
                            "timestamp": datetime.now().isoformat()
                        })

        except Exception as e:
            print(f"[Twitter] Error scraping @{account}: {e}")

    return all_posts


# ==================================================
# PART 4: NEWS SCRAPING
# ==================================================

def scrape_train_news():
    """Scrape news about Mumbai local trains."""
    print("[News] Scraping train-related news...")

    news_items = []

    # Try Google News search
    try:
        query = "Mumbai local train"
        url = f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article titles
            articles = soup.find_all('article')

            for article in articles[:10]:
                title_elem = article.find('a', class_='JtKRv')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    news_items.append({
                        "title": title,
                        "source": "Google News",
                        "timestamp": datetime.now().isoformat()
                    })

    except Exception as e:
        print(f"[News] Error: {e}")

    return news_items


# ==================================================
# SCRAPED REVIEWS STORAGE
# ==================================================

def load_scraped_reviews():
    """Load scraped reviews from JSON file."""
    if os.path.exists(SCRAPED_REVIEWS_FILE):
        with open(SCRAPED_REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"reviews": [], "twitter": [], "news": [], "last_updated": None}


def save_scraped_reviews(data):
    """Save scraped reviews to JSON file."""
    data["last_updated"] = datetime.now().isoformat()
    with open(SCRAPED_REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_scraped_data():
    """Update all scraped data."""
    print("=" * 50)
    print("Updating scraped reviews and posts...")
    print("=" * 50)

    data = load_scraped_reviews()

    # Scrape Twitter
    twitter_posts = scrape_twitter_posts("Mumbai local train delay", limit=10)
    twitter_posts += scrape_twitter_posts("#MumbaiLocal", limit=10)
    twitter_posts += scrape_railway_twitter()
    data["twitter"] = twitter_posts

    # Scrape news
    news = scrape_train_news()
    data["news"] = news

    # Save
    save_scraped_reviews(data)

    print(f"\nUpdated: {len(twitter_posts)} tweets, {len(news)} news items")
    return data


# ==================================================
# REVIEW SUMMARY FOR CHATBOT
# ==================================================

def get_review_summary(subject):
    """Get a formatted review summary for the chatbot."""
    reviews = get_reviews_for(subject)

    if not reviews:
        return None

    avg_rating = get_average_rating(subject)

    summary = f"\n\n📊 **Reviews for {subject}**\n"

    if avg_rating:
        stars = "⭐" * round(avg_rating)
        summary += f"Average Rating: {stars} ({avg_rating:.1f}/5)\n\n"

    # Show latest 3 reviews
    latest = sorted(reviews, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]

    for r in latest:
        rating_str = f"{'⭐' * r['rating']}" if r.get('rating') else ""
        summary += f"• {rating_str} _{r.get('comment', r.get('text', 'No comment'))[:100]}_\n"

    if len(reviews) > 3:
        summary += f"\n_...and {len(reviews) - 3} more reviews_"

    return summary


# ==================================================
# MAIN - For testing
# ==================================================

if __name__ == "__main__":
    # Test adding a review
    print("Testing review system...")

    # Add sample review
    review = add_user_review(
        category="station",
        subject="Andheri Station",
        rating=4,
        comment="Clean platforms, but very crowded during peak hours.",
        username="TestUser"
    )
    print(f"Added review: {review}")

    # Get reviews
    reviews = get_reviews_for("Andheri")
    print(f"Reviews for Andheri: {len(reviews)}")

    # Update scraped data
    update_scraped_data()
