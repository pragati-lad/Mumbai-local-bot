# app.py (full) - includes authentication using streamlit-authenticator
import streamlit as st
import base64
from train_chatbot_enhanced import chatbot_response
from google_sheets_reviews import (
    add_review_to_sheets as add_user_review,
    add_user_to_sheets,
    get_reviews_for_subject as get_reviews_for,
    get_review_summary_sheets as get_review_summary,
    get_all_reviews_from_sheets,
    check_sheets_connection
)

try:
    from nlp_sentiment import (
        analyze_sentiment, analyze_reviews_batch,
        get_sentiment_summary, format_sentiment_bar
    )
    NLP_SENTIMENT_AVAILABLE = True
except ImportError:
    NLP_SENTIMENT_AVAILABLE = False

# ---------------- Authentication (streamlit-authenticator) ----------------
try:
    import streamlit_authenticator as stauth
except Exception:
    stauth = None
    print("streamlit-authenticator not installed. Run: pip install streamlit-authenticator")

def _load_credentials():
    """Load credentials dict from st.secrets or session_state fallback."""
    if hasattr(st, "secrets") and st.secrets.get("auth"):
        return dict(st.secrets["auth"])
    return st.session_state.get("credentials", {"usernames": {}})

def _save_credentials_in_session(creds):
    st.session_state["credentials"] = creds

# signature_key from secrets recommended
SIGNATURE_KEY = None
if hasattr(st, "secrets") and st.secrets.get("auth_signature_key"):
    SIGNATURE_KEY = st.secrets["auth_signature_key"]
else:
    # fallback key for dev (replace with secret in production)
    SIGNATURE_KEY = st.session_state.get("auth_signature_key", "change_this_signature_key")

# cookie name
COOKIE_NAME = "mumbai_local_auth"

credentials = _load_credentials()

if stauth is None:
    st.warning("Authentication library not available — app will run without login. Install streamlit-authenticator for secure login.")
    authenticated_user = True
    current_user_name = "Guest"
else:
    # if no credentials exist, show a quick registration to create first user (in-memory)
    if not credentials.get("usernames"):
        st.info("No users found — create an admin account to get started.")
        with st.form("register_first"):
            new_name = st.text_input("Full name")
            new_email = st.text_input("Email (will be username)")
            new_password = st.text_input("Password", type="password")
            create = st.form_submit_button("Create account")
            if create:
                if not new_name or not new_email or not new_password:
                    st.error("Please fill all fields")
                    st.stop()
                # hash password and add to credentials
                hashed = stauth.Hasher([new_password]).generate()[0]
                credentials = {"usernames": {
                    new_email: {"name": new_name, "password": hashed}
                }}
                _save_credentials_in_session(credentials)
                # record user in sheet (best-effort)
                try:
                    add_user_to_sheets(new_name, new_email, provider="local")
                except Exception:
                    pass
                st.success("Account created — please login below.")
                st.experimental_rerun()

    authenticator = stauth.Authenticate(credentials, COOKIE_NAME, SIGNATURE_KEY, cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status is None:
        st.warning("Please enter your username and password")
        st.stop()
    elif authentication_status is False:
        st.error("Username/password is incorrect")
        # show optional registration button
        if st.button("Register a new account"):
            st.session_state.show_register = True
        st.stop()
    else:
        # successful login
        current_user_name = name
        # record login into users sheet (best-effort)
        try:
            add_user_to_sheets(name, username, provider="local")
        except Exception:
            pass
        # expose a logout button in the sidebar
        with st.sidebar:
            authenticator.logout("Logout", "sidebar")
        authenticated_user = True

    # optional registration flow (if user clicked Register)
    if st.session_state.get("show_register"):
        st.header("Register")
        new_name = st.text_input("Full name", key="reg_name")
        new_email = st.text_input("Email (will be username)", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Create account", key="reg_create"):
            if not new_name or not new_email or not new_password:
                st.error("Fill all fields")
            else:
                hashed = stauth.Hasher([new_password]).generate()[0]
                creds = _load_credentials()
                creds.setdefault("usernames", {})[new_email] = {"name": new_name, "password": hashed}
                _save_credentials_in_session(creds)
                # record to sheets
                try:
                    add_user_to_sheets(new_name, new_email, provider="local")
                except Exception:
                    pass
                st.success("Account created — please login.")
                st.session_state.show_register = False
                st.experimental_rerun()

# ---------------- Dynamic Suggestions ----------------
SUGGESTIONS = {
    "default": [
        "Andheri to Churchgate",
        "Thane to CSMT",
        "Dadar to Kalyan",
        "Kurla to Panvel",
        "AC trains available?",
        "Monthly pass price",
        "Student concession",
        "Luggage rules",
    ],
    "western": [
        "Bandra to Virar",
        "Borivali to Churchgate",
        "Dadar to Andheri",
        "Churchgate to Borivali",
        "AC on Western line",
        "Reviews for Andheri",
    ],
    "central": [
        "CSMT to Kalyan",
        "Thane to Dadar",
        "Ghatkopar to CSMT",
        "Kurla to Thane",
        "Dadar to Dombivli",
        "Reviews for Thane",
    ],
    "harbour": [
        "CSMT to Panvel",
        "Vashi to CSMT",
        "Kurla to Vashi",
        "Panvel to Kurla",
        "Belapur to CSMT",
        "Reviews for Vashi",
    ],
    "ac": [
        "AC trains Western line",
        "AC trains Central line",
        "AC from Churchgate",
        "AC from Virar",
        "AC local info",
        "AC ticket price",
    ],
    "info": [
        "Monthly pass price",
        "Student concession",
        "Senior citizen discount",
        "Luggage rules",
        "AC trains info",
        "Andheri to Churchgate",
    ],
}

# Station list for reviews
STATIONS = [
    "Churchgate", "Dadar", "Bandra", "Andheri", "Borivali", "Virar",
    "CSMT", "Thane", "Kalyan", "Kurla", "Ghatkopar", "Dombivli",
    "Panvel", "Vashi", "Belapur"
]


def get_related_suggestions(query):
    q = query.lower()
    if "ac" in q or "air condition" in q:
        return SUGGESTIONS["ac"]
    if any(word in q for word in ["pass", "concession", "student", "senior", "luggage", "rule"]):
        return SUGGESTIONS["info"]
    western_stations = ["churchgate", "bandra", "andheri", "borivali", "virar", "dadar", "malad", "goregaon"]
    if any(station in q for station in western_stations):
        central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "dombivli"]
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in central_stations + harbour_stations):
            return SUGGESTIONS["western"]
    central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "kurla", "dombivli", "mulund"]
    if any(station in q for station in central_stations):
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in harbour_stations):
            return SUGGESTIONS["central"]
    harbour_stations = ["panvel", "vashi", "belapur", "nerul", "sanpada"]
    if any(station in q for station in harbour_stations):
        return SUGGESTIONS["harbour"]
    return SUGGESTIONS["default"]


# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local",
    page_icon="🚊",
    layout="wide"
)

# ---------------- CSS - Glassmorphism Mumbai Theme ----------------
import pathlib
_bg_path = pathlib.Path(__file__).parent / "bg.jpg"
_bg_b64 = base64.b64encode(_bg_path.read_bytes()).decode()

css_template = """
<style>
/* (same CSS as before) */
</style>
""".format(bg_b64=_bg_b64)

st.markdown(css_template, unsafe_allow_html=True)

# ---------------- Layout: Main + Sidebar ----------------
main_col, review_col = st.columns([2, 1])

# ==================================================
# MAIN COLUMN - CHATBOT
# ==================================================
with main_col:
    st.markdown('<div class="main-title">Apna Mumbai Local</div>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge western">Western</span>
        <span class="line-badge central">Central</span>
        <span class="line-badge harbour">Harbour</span>
        <br>Your pocket train guide - 7,500+ trains
    </p>''', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "suggestions" not in st.session_state:
        st.session_state.suggestions = SUGGESTIONS["default"]

    if "chat_context" not in st.session_state:
        st.session_state.chat_context = {}

    if len(st.session_state.messages) == 0:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "Hey! Welcome to Apna Mumbai Local!\n\n"
                    "Need train timings? Platform info? I got you covered!"
                )
            }
        )

    for msg in st.session_state.messages:
        avatar = "🚃" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Where to? Try: Dadar to Thane...")

    st.markdown('<p style="color:#64748b ...">Try These</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, s in enumerate(st.session_state.suggestions[:8]):
        if cols[i % 4].button(s, key=f"sugg_{i}"):
            user_input = s

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        if "review" in user_input.lower() or "kaisa" in user_input.lower():
            for station in STATIONS:
                if station.lower() in user_input.lower():
                    review_summary = get_review_summary(station)
                    if review_summary:
                        response = f"**{station} Station**\n" + review_summary
                    else:
                        response = f"No reviews for {station} yet. Be the first!"
                    break
            else:
                response = "Which station? Try: *Reviews for Andheri*"
        else:
            response = chatbot_response(user_input, context=st.session_state.chat_context)

        with st.chat_message("assistant", avatar="🚃"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.suggestions = get_related_suggestions(user_input)
        st.rerun()

# ==================================================
# REVIEW COLUMN - SUBMIT & VIEW REVIEWS
# ==================================================
with review_col:
    st.markdown('<p class="section-header">Spill the Tea!</p>', unsafe_allow_html=True)

    if "star_rating" not in st.session_state:
        st.session_state.star_rating = 4
    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    star_cols = st.columns(5)
    for i in range(5):
        with star_cols[i]:
            if st.button("★" if i < st.session_state.star_rating else "☆", key=f"star_{i}"):
                st.session_state.star_rating = i + 1
                st.rerun()
    review_rating = st.session_state.star_rating

    # Review Form — includes photos uploader inside form
    with st.form(f"review_form_{st.session_state.form_key}"):
        review_comment = st.text_area("Your review", placeholder="Go ahead and gossip...", max_chars=500)
        review_name = st.text_input("Name", placeholder="Anonymous")
        photos = st.file_uploader("Attach station photos (optional)", type=["jpg","jpeg","png"], accept_multiple_files=True, label_visibility="visible")

        submitted = st.form_submit_button("Post It!", use_container_width=True)

        if submitted and review_comment:
            sentiment_data = None
            if NLP_SENTIMENT_AVAILABLE:
                sentiment_data = analyze_sentiment(review_comment)

            # prepare photo tuples (filename, bytes)
            photo_tuples = []
            if photos:
                for p in photos:
                    try:
                        data = p.getvalue()
                    except Exception:
                        p.seek(0)
                        data = p.read()
                    photo_tuples.append((p.name, data))

            try:
                result = add_user_review(
                    category="general",
                    subject="General",
                    rating=review_rating,
                    comment=review_comment,
                    username=review_name if review_name else "Anonymous",
                    photos=photo_tuples
                )
            except Exception as e:
                st.warning(f"Could not save review: {e}")
                result = None

            st.session_state.star_rating = 4
            st.session_state.form_key += 1
            if result and isinstance(result, dict) and result.get('id') is not None:
                if sentiment_data:
                    st.toast(f"Review added! {sentiment_data['label']}")
                else:
                    st.toast("Review added!")
            else:
                st.warning("Could not save review. Try again.")
            st.rerun()

    st.markdown("---")
    st.markdown('<p class="section-header">Station Snaps</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="section-header">Spilled Tea</p>', unsafe_allow_html=True)

    # Get reviews and coerce/validate to a list of dicts
    user_reviews = get_all_reviews_from_sheets()

    # Normalize user_reviews to a list so sorting and iteration are safe
    if not user_reviews:
        user_reviews = []
    elif isinstance(user_reviews, dict):
        user_reviews = [user_reviews]
    elif not isinstance(user_reviews, list):
        try:
            user_reviews = list(user_reviews)
        except Exception:
            user_reviews = []

    if user_reviews:
        if NLP_SENTIMENT_AVAILABLE:
            try:
                user_reviews = analyze_reviews_batch(user_reviews)
            except Exception:
                pass
            try:
                summary = get_sentiment_summary(user_reviews)
                st.markdown(format_sentiment_bar(summary), unsafe_allow_html=True)
            except Exception:
                pass

        valid_reviews = [r for r in user_reviews if isinstance(r, dict)]
        try:
            sorted_reviews = sorted(valid_reviews, key=lambda x: str(x.get('timestamp','') or ''), reverse=True)[:5]
        except Exception:
            sorted_reviews = valid_reviews[-5:]

        for review in sorted_reviews:
            try:
                rating_val = int(review.get("rating", 0)) if review.get("rating") is not None else 0
            except Exception:
                rating_val = 0
            rating_val = max(0, min(5, rating_val))
            stars = "★" * rating_val + "☆" * (5 - rating_val)

            sentiment_html = ""
            if NLP_SENTIMENT_AVAILABLE and isinstance(review.get("sentiment", None), dict):
                s = review["sentiment"]
                sentiment_html = f'<span style="color:{s.get("color","")}; float:right; font-size:0.8rem;">{s.get("label","")}</span>'

            comment = review.get('comment') or ''
            username = review.get('username') or 'Anonymous'

            st.markdown(f"""
            <div class="review-card">
                <span class="stars">{stars}</span>{sentiment_html}<br>
                <small>{comment[:150]}</small><br>
                <small>— {username}</small>
            </div>
            """, unsafe_allow_html=True)

            # Render photos if present
            photos = review.get('photos') or []
            if isinstance(photos, str) and photos:
                photos = [p.strip() for p in photos.split(',') if p.strip()]

            if photos:
                cols = st.columns(min(4, len(photos)))
                for i, p_url in enumerate(photos[:4]):
                    try:
                        cols[i].image(p_url, use_column_width=True)
                    except Exception:
                        cols[i].markdown(f"[view image]({p_url})")
    else:
        st.markdown("""
        <div class="review-card" style="text-align: center;">
            No reviews yet!<br>
            <small style="color: #636e72;">common bro drop a comment!</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        print(f"SHEETS_URL: {connection.get('spreadsheet_url', '')}")
        st.caption("⟳ synced")
    else:
        st.caption("◇ local")
