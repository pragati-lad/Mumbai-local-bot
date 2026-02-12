# ==================================================
# Mumbai Local Train - Google Sheets Review Storage
# ==================================================
# Permanent storage for user reviews using Google Sheets
# ==================================================

import json
import os
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("Warning: gspread not installed. Run: pip install gspread google-auth")

# ---------------- CONFIGURATION ----------------

# Google Sheets settings
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Sheet names
REVIEWS_SHEET = "User Reviews"
SCRAPED_SHEET = "Scraped Data"

# Cache for performance
_sheet_cache = {}
_last_fetch = {}
CACHE_DURATION = 60  # seconds

# Scraped reviews file
SCRAPED_REVIEWS_FILE = os.path.join(os.path.dirname(__file__), "scraped_reviews.json")


def get_credentials():
    """Get Google credentials from Streamlit secrets or local file."""

    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception as e:
        print(f"Sheets credentials error: {e}")

    # Try environment variable
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    # Try local file
    creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(creds_file):
        return Credentials.from_service_account_file(creds_file, scopes=SCOPES)

    return None


def get_client():
    """Get authenticated gspread client."""
    if not GSPREAD_AVAILABLE:
        return None

    creds = get_credentials()
    if creds:
        return gspread.authorize(creds)
    return None


def get_or_create_spreadsheet(client, name="Mumbai Train Reviews"):
    """Get existing spreadsheet or create new one."""
    try:
        # Try to open existing
        spreadsheet = client.open(name)
    except gspread.SpreadsheetNotFound:
        # Create new
        spreadsheet = client.create(name)
        # Make it accessible
        spreadsheet.share(None, perm_type='anyone', role='reader')

        # Create Reviews sheet with headers
        reviews_sheet = spreadsheet.sheet1
        reviews_sheet.update_title(REVIEWS_SHEET)
        reviews_sheet.append_row([
            'ID', 'Timestamp', 'Category', 'Subject',
            'Rating', 'Comment', 'Username', 'Source'
        ])

        # Create Scraped Data sheet
        scraped_sheet = spreadsheet.add_worksheet(title=SCRAPED_SHEET, rows=1000, cols=10)
        scraped_sheet.append_row([
            'ID', 'Timestamp', 'Type', 'Content', 'Source', 'Extra'
        ])

    return spreadsheet


# ==================================================
# REVIEW OPERATIONS
# ==================================================

def add_review_to_sheets(category, subject, rating, comment, username="Anonymous"):
    """Add a review to Google Sheets."""
    client = get_client()
    if not client:
        print("Google Sheets not configured, using local storage")
        return _add_review_local(category, subject, rating, comment, username)

    try:
        spreadsheet = get_or_create_spreadsheet(client)
        sheet = spreadsheet.worksheet(REVIEWS_SHEET)

        # Get next ID
        all_values = sheet.get_all_values()
        next_id = len(all_values)

        # Add row
        row = [
            next_id,
            datetime.now().isoformat(),
            category,
            subject,
            rating,
            comment,
            username,
            'user'
        ]
        sheet.append_row(row)

        # Clear cache
        _sheet_cache.pop('reviews', None)

        return {
            'id': next_id,
            'category': category,
            'subject': subject,
            'rating': rating,
            'comment': comment,
            'username': username,
            'timestamp': row[1],
            'source': 'user'
        }

    except Exception as e:
        print(f"Error adding to Google Sheets: {e}")
        return _add_review_local(category, subject, rating, comment, username)


def get_all_reviews_from_sheets():
    """Get all reviews from Google Sheets."""
    # Check cache
    cache_key = 'reviews'
    now = datetime.now().timestamp()

    if cache_key in _sheet_cache:
        if now - _last_fetch.get(cache_key, 0) < CACHE_DURATION:
            return _sheet_cache[cache_key]

    client = get_client()
    if not client:
        return _get_reviews_local()

    try:
        spreadsheet = get_or_create_spreadsheet(client)
        sheet = spreadsheet.worksheet(REVIEWS_SHEET)

        # Get all data
        records = sheet.get_all_records()

        reviews = []
        for record in records:
            reviews.append({
                'id': record.get('ID'),
                'timestamp': record.get('Timestamp'),
                'category': record.get('Category'),
                'subject': record.get('Subject'),
                'rating': int(record.get('Rating', 0)) if record.get('Rating') else 0,
                'comment': record.get('Comment'),
                'username': record.get('Username'),
                'source': record.get('Source', 'user')
            })

        # Update cache
        _sheet_cache[cache_key] = reviews
        _last_fetch[cache_key] = now

        return reviews

    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        return _get_reviews_local()


def get_reviews_for_subject(subject):
    """Get reviews for a specific station/route from all sources."""
    # Get both user and scraped reviews
    all_reviews = get_all_reviews_combined()
    subject_lower = subject.lower()

    matching = []
    for review in all_reviews:
        # Check subject field
        if subject_lower in review.get('subject', '').lower():
            matching.append(review)
        # Also check comment content for scraped reviews
        elif subject_lower in review.get('comment', '').lower():
            matching.append(review)

    return matching


def get_average_rating_sheets(subject):
    """Get average rating for a subject."""
    reviews = get_reviews_for_subject(subject)
    if not reviews:
        return None

    ratings = [r['rating'] for r in reviews if r.get('rating')]
    if not ratings:
        return None

    return sum(ratings) / len(ratings)


def get_review_summary_sheets(subject):
    """Get formatted review summary for chatbot."""
    reviews = get_reviews_for_subject(subject)

    if not reviews:
        return None

    avg_rating = get_average_rating_sheets(subject)

    # Count sources
    user_reviews = [r for r in reviews if r.get('source') == 'user']
    scraped_reviews = [r for r in reviews if r.get('source') != 'user']

    summary = f"\n\n📊 **Reviews for {subject}**\n"

    if avg_rating:
        stars = "⭐" * round(avg_rating)
        summary += f"Average Rating: {stars} ({avg_rating:.1f}/5)\n"
        summary += f"_{len(user_reviews)} user reviews, {len(scraped_reviews)} from social media_\n\n"

    # Show latest 3 reviews, prioritizing user reviews
    sorted_reviews = sorted(reviews, key=lambda x: (
        0 if x.get('source') == 'user' else 1,  # User reviews first
        x.get('timestamp', '')  # Then by time
    ), reverse=True)[:3]

    for r in sorted_reviews:
        rating_str = f"{'⭐' * r['rating']}" if r.get('rating') else ""
        comment = r.get('comment', 'No comment')[:100]
        source_tag = ""
        if r.get('source') and r.get('source') != 'user':
            source_tag = f" [{r.get('source', '').split('/')[0]}]"
        summary += f"• {rating_str} _{comment}_{source_tag}\n"

    if len(reviews) > 3:
        summary += f"\n_...and {len(reviews) - 3} more reviews_"

    return summary


# ==================================================
# SCRAPED REVIEWS LOADER
# ==================================================

def get_scraped_reviews():
    """Load scraped reviews from JSON file."""
    if os.path.exists(SCRAPED_REVIEWS_FILE):
        try:
            with open(SCRAPED_REVIEWS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('reviews', [])
        except Exception as e:
            print(f"Error loading scraped reviews: {e}")
    return []


def get_all_reviews_combined():
    """Get all reviews from Google Sheets + scraped data."""
    user_reviews = get_all_reviews_from_sheets()
    scraped_reviews = get_scraped_reviews()

    # Combine both sources
    all_reviews = user_reviews + scraped_reviews
    return all_reviews


# ==================================================
# LOCAL FALLBACK (when Google Sheets not available)
# ==================================================

def _get_local_file():
    return os.path.join(os.path.dirname(__file__), 'user_reviews.json')


def _get_reviews_local():
    """Fallback: Load from local JSON."""
    filepath = _get_local_file()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('reviews', [])
    return []


def _add_review_local(category, subject, rating, comment, username):
    """Fallback: Add to local JSON."""
    filepath = _get_local_file()

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'reviews': []}

    review = {
        'id': len(data['reviews']) + 1,
        'category': category,
        'subject': subject,
        'rating': rating,
        'comment': comment,
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'source': 'user'
    }

    data['reviews'].append(review)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return review


# ==================================================
# CHECK CONNECTION
# ==================================================

def check_sheets_connection():
    """Check if Google Sheets is properly configured."""
    client = get_client()
    if not client:
        return {
            'connected': False,
            'error': 'No credentials found. Check credentials.json or Streamlit secrets.'
        }

    try:
        spreadsheet = get_or_create_spreadsheet(client)
        return {
            'connected': True,
            'spreadsheet_name': spreadsheet.title,
            'spreadsheet_url': spreadsheet.url
        }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }


# ==================================================
# MAIN - Setup instructions
# ==================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Google Sheets Review Storage - Setup")
    print("=" * 60)

    print("""
To set up Google Sheets storage:

1. Go to Google Cloud Console: https://console.cloud.google.com/

2. Create a new project or select existing

3. Enable APIs:
   - Google Sheets API
   - Google Drive API

4. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name, click "Create"
   - Skip optional steps, click "Done"

5. Create Key:
   - Click on the service account you created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key" > "JSON"
   - Download the JSON file

6. For Local Development:
   - Save the JSON file as 'credentials.json' in this folder

7. For Streamlit Cloud:
   - Go to your app's Settings > Secrets
   - Add the JSON content under [gcp_service_account]:

   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
   client_email = "...@...iam.gserviceaccount.com"
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "..."
""")

    print("\nChecking connection...")
    status = check_sheets_connection()

    if status['connected']:
        print(f"✅ Connected to: {status['spreadsheet_name']}")
        print(f"📊 URL: {status['spreadsheet_url']}")
    else:
        print(f"❌ Not connected: {status['error']}")
