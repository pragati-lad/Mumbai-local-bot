# google_sheets_reviews.py
import json
import os
import io
import time
from datetime import datetime
from typing import List, Tuple

# Drive client
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    DRIVE_AVAILABLE = True
except Exception:
    DRIVE_AVAILABLE = False

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("Warning: gspread not installed. Run: pip install gspread google-auth")

# ---------------- CONFIGURATION ----------------

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SPREADSHEET_ID = "1gUX2KN0nMQKsNRe61vo6z89h9b3JQ9eeoNru46lJD3k"
REVIEWS_SHEET = "reviews"
SCRAPED_SHEET = "Scraped Data"

_sheet_cache = {}
_last_fetch = {}
CACHE_DURATION = 60

SCRAPED_REVIEWS_FILE = os.path.join(os.path.dirname(__file__), "scraped_reviews.json")

# local uploads dir for fallback
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_credentials():
    """Get Google credentials from Streamlit secrets or local file."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            # fix escaped newlines
            if 'private_key' in creds_dict:
                pk = creds_dict['private_key']
                pk = pk.replace('\\n', '\n')
                pk = pk.strip()
                # debug prints intentionally short
                print(f"PEM key starts with: {pk[:30]}...")
                print(f"PEM key ends with: ...{pk[-30:]}")
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception as e:
        print(f"Sheets credentials error (secrets): {e}")

    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except Exception as e:
            print(f"Sheets credentials error (env): {e}")

    creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(creds_file):
        try:
            return Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        except Exception as e:
            print(f"Sheets credentials error (file): {e}")

    return None


def get_client():
    """Get authenticated gspread client."""
    if not GSPREAD_AVAILABLE:
        return None

    creds = get_credentials()
    if creds:
        try:
            return gspread.authorize(creds)
        except Exception as e:
            print(f"gspread authorize error: {e}")
    return None


def get_or_create_spreadsheet(client):
    """Open the existing spreadsheet by ID."""
    return client.open_by_key(SPREADSHEET_ID)


# ---------------- Drive helpers ----------------

def get_drive_service():
    """Return an authenticated Drive v3 service or None."""
    if not DRIVE_AVAILABLE:
        return None
    creds = get_credentials()
    if not creds:
        return None
    try:
        return build('drive', 'v3', credentials=creds, cache_discovery=False)
    except Exception as e:
        print(f"Drive service init failed: {e}")
        return None


def upload_files_to_drive(file_tuples: List[Tuple[str, bytes]], folder_id: str = None) -> List[str]:
    """
    Upload files to Drive and return shareable urls.
    file_tuples: list of (filename, bytes)
    """
    svc = get_drive_service()
    urls = []
    if not svc:
        return urls

    for filename, content in file_tuples:
        try:
            fh = io.BytesIO(content)
            media = MediaIoBaseUpload(fh, mimetype='image/jpeg', resumable=False)
            metadata = {'name': filename}
            if folder_id:
                metadata['parents'] = [folder_id]
            created = svc.files().create(body=metadata, media_body=media, fields='id, webViewLink, webContentLink').execute()
            file_id = created.get('id')

            # Make it shareable (anyone with link)
            try:
                svc.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
            except Exception as pe:
                print(f"Could not set permission for {file_id}: {pe}")

            link = created.get('webViewLink') or created.get('webContentLink') or f"https://drive.google.com/file/d/{file_id}/view"
            urls.append(link)
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")
    return urls


def _save_photos_locally(file_tuples: List[Tuple[str, bytes]]) -> List[str]:
    """Save photos to local uploads dir and return local paths."""
    urls = []
    for filename, content in file_tuples:
        safe = f"{int(time.time())}_{filename}"
        path = os.path.join(UPLOADS_DIR, safe)
        try:
            with open(path, 'wb') as f:
                f.write(content)
            urls.append(path)
        except Exception as e:
            print(f"Failed saving {filename} locally: {e}")
    return urls


# ==================================================
# REVIEW OPERATIONS
# ==================================================

def add_review_to_sheets(category, subject, rating, comment, username="Anonymous", photos: List[Tuple[str, bytes]] = None):
    """Add a review to Google Sheets and optionally upload photos.

    photos: optional list of (filename, bytes)
    """
    client = get_client()
    timestamp = datetime.now().isoformat()
    if not client:
        # fallback: raise or return local storage structure
        # keep behavior similar to original: raise to indicate misconfig
        raise RuntimeError("Google Sheets client could not be initialized. Check Streamlit secrets and installed dependencies.")

    try:
        spreadsheet = get_or_create_spreadsheet(client)
        sheet = spreadsheet.worksheet(REVIEWS_SHEET)

        all_values = sheet.get_all_values()
        next_id = len(all_values)

        # handle photos: try Drive first, else local
        photo_urls = []
        if photos:
            try:
                photo_urls = upload_files_to_drive(photos)
            except Exception as e:
                print(f"Drive upload exception: {e}")
                photo_urls = []

            if not photo_urls:
                # fallback: save locally
                try:
                    photo_urls = _save_photos_locally(photos)
                except Exception as e:
                    print(f"Local save failed: {e}")
                    photo_urls = []

        photos_cell = ",".join(photo_urls) if photo_urls else ""

        row = [
            next_id,
            timestamp,
            category,
            subject,
            rating,
            comment,
            username,
            'user',
            photos_cell
        ]
        sheet.append_row(row)

        # Invalidate cache
        _sheet_cache.pop('reviews', None)

        return {
            'id': next_id,
            'category': category,
            'subject': subject,
            'rating': rating,
            'comment': comment,
            'username': username,
            'timestamp': timestamp,
            'source': 'user',
            'photos': photo_urls
        }

    except Exception as e:
        print(f"Error adding to Google Sheets: {e}")
        raise


def _normalize_header_key(k: str) -> str:
    if k is None:
        return ''
    return k.strip().lower()


def get_all_reviews_from_sheets():
    """Get all reviews from Google Sheets (robust to header differences)."""
    cache_key = 'reviews'
    now = datetime.now().timestamp()

    if cache_key in _sheet_cache:
        if now - _last_fetch.get(cache_key, 0) < CACHE_DURATION:
            return _sheet_cache[cache_key]

    client = get_client()
    if not client:
        return []

    try:
        spreadsheet = get_or_create_spreadsheet(client)
        sheet = spreadsheet.worksheet(REVIEWS_SHEET)

        # Try get_all_records (works when a header row exists)
        try:
            records = sheet.get_all_records()
        except Exception:
            records = []

        reviews = []

        if records and isinstance(records, list) and isinstance(records[0], dict):
            # Normalize keys and populate fields using flexible header matching
            for record in records:
                norm = {k.strip().lower(): v for k, v in record.items() if k is not None}
                # rating may be string; safe parse
                try:
                    rating_val = int(norm.get('rating')) if norm.get('rating') not in (None, '') else 0
                except Exception:
                    rating_val = 0
                photos_field = norm.get('photos') or norm.get('photo') or ''
                photos_list = [p.strip() for p in str(photos_field).split(',') if p.strip()] if photos_field else []
                reviews.append({
                    'id': norm.get('id'),
                    'timestamp': norm.get('timestamp') or norm.get('time') or '',
                    'category': norm.get('category') or '',
                    'subject': norm.get('subject') or '',
                    'rating': rating_val,
                    'comment': norm.get('comment') or norm.get('comments') or norm.get('text') or '',
                    'username': norm.get('username') or norm.get('user') or 'Anonymous',
                    'source': norm.get('source') or 'user',
                    'photos': photos_list
                })
        else:
            # fallback: read by raw values (no header or header missing)
            all_values = sheet.get_all_values()
            if not all_values:
                _sheet_cache[cache_key] = []
                _last_fetch[cache_key] = now
                return []

            header_row = all_values[0]
            header = [h.strip().lower() for h in header_row]
            # helper to find column index for a header candidate
            def col_index(*names):
                for n in names:
                    if n in header:
                        return header.index(n)
                return None

            idx_id = col_index('id', 'index', 'no')
            idx_ts = col_index('timestamp', 'time', 'date')
            idx_cat = col_index('category',)
            idx_sub = col_index('subject', 'title')
            idx_rating = col_index('rating', 'stars')
            idx_comment = col_index('comment', 'comments', 'text', 'review')
            idx_user = col_index('username', 'user', 'author')
            idx_source = col_index('source')
            idx_photos = col_index('photos', 'photo', 'images')

            for row in all_values[1:]:
                def safe_get(idx):
                    if idx is None:
                        return ''
                    if idx < len(row):
                        return row[idx]
                    return ''

                try:
                    rating_raw = safe_get(idx_rating)
                    rating_val = int(rating_raw) if (rating_raw not in (None, '')) else 0
                except Exception:
                    rating_val = 0

                photos_cell = safe_get(idx_photos) or ''
                photos_list = [p.strip() for p in str(photos_cell).split(',') if p.strip()] if photos_cell else []

                reviews.append({
                    'id': safe_get(idx_id) or None,
                    'timestamp': safe_get(idx_ts) or '',
                    'category': safe_get(idx_cat) or '',
                    'subject': safe_get(idx_sub) or '',
                    'rating': rating_val,
                    'comment': safe_get(idx_comment) or '',
                    'username': safe_get(idx_user) or 'Anonymous',
                    'source': safe_get(idx_source) or 'user',
                    'photos': photos_list
                })

        _sheet_cache[cache_key] = reviews
        _last_fetch[cache_key] = now
        return reviews

    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        return []


def get_reviews_for_subject(subject):
    """Get reviews for a specific station/route from all sources."""
    all_reviews = get_all_reviews_from_sheets()
    subject_lower = subject.lower()

    matching = []
    for review in all_reviews:
        if subject_lower in (review.get('subject') or '').lower():
            matching.append(review)
        elif subject_lower in (review.get('comment') or '').lower():
            matching.append(review)

    return matching


def get_average_rating_sheets(subject):
    """Get average rating for a subject."""
    reviews = get_reviews_for_subject(subject)
    if not reviews:
        return None

    ratings = [r['rating'] for r in reviews if r.get('rating') is not None]
    if not ratings:
        return None

    return sum(ratings) / len(ratings)


def get_review_summary_sheets(subject):
    """Get formatted review summary for chatbot."""
    reviews = get_reviews_for_subject(subject)

    if not reviews:
        return None

    avg_rating = get_average_rating_sheets(subject)

    user_reviews = [r for r in reviews if r.get('source') == 'user']
    scraped_reviews = [r for r in reviews if r.get('source') != 'user']

    summary = f"\n\n📊 **Reviews for {subject}**\n"

    if avg_rating:
        stars = "⭐" * round(avg_rating)
        summary += f"Average Rating: {stars} ({avg_rating:.1f}/5)\n"
        summary += f"_{len(user_reviews)} user reviews, {len(scraped_reviews)} from social media_\n\n"

    sorted_reviews = sorted(reviews, key=lambda x: (
        0 if x.get('source') == 'user' else 1,
        x.get('timestamp', '')
    ), reverse=True)[:3]

    for r in sorted_reviews:
        rating_str = f"{'⭐' * r['rating']}" if r.get('rating') else ""
        comment = (r.get('comment') or 'No comment')[:100]
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
    return user_reviews + scraped_reviews


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
