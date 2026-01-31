import streamlit as st
import time
from difflib import get_close_matches

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# --------------------------------------------------
# DATA
# --------------------------------------------------

WR_STATIONS = [
    "Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central",
    "Mahalakshmi", "Lower Parel", "Prabhadevi", "Dadar", "Matunga Road",
    "Mahim Junction", "Bandra", "Khar Road", "Santacruz", "Vile Parle",
    "Andheri", "Jogeshwari", "Goregaon", "Malad", "Kandivali",
    "Borivali", "Dahisar", "Mira Road", "Bhayandar",
    "Vasai Road", "Nalla Sopara", "Virar"
]

HARBOUR_STATIONS = [
    "CSMT", "Masjid", "Sandhurst Road", "Dockyard Road",
    "Sewri", "Vadala Road", "Kurla", "Chembur",
    "Govandi", "Mankhurd", "Vashi", "Sanpada",
    "Belapur CBD", "Panvel"
]

ALL_STATIONS = WR_STATIONS + HARBOUR_STATIONS

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
    "andheri west": ["Andheri"],
    "andheri east": ["Andheri"],
}

# --------------------------------------------------
# UI HEADER
# --------------------------------------------------

st.title("Mumbai Local Train Assistant")
st.caption("Routes • Stations • Railway guidance")

st.markdown("### Suggested queries")
suggested_queries = [
    "Virar to Churchgate",
    "Panvel to CSMT",
    "Virar to Malabar Hills",
    "Andheri to Bandra",
    "What are luggage rules?"
]

cols = st.columns(2)
for i, q in enumerate(suggested_queries):
    if cols[i % 2].button(q):
        st.session_state.user_query = q

st.divider()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text):
    return text.lower().strip()

def fuzzy_station_match(word):
    matches = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.7)
    return matches[0] if matches else None

def extract_stations(query):
    words = query.split()
    found = []
    for w in words:
        match = fuzzy_station_match(w.title())
        if match and match not in found:
            found.append(match)
    return found

def find_nearby_location(query):
    q = normalize(query)
    for place, stations in NEARBY_LOCATIONS.items():
        if place in q:
            return place.title(), stations
    return None, None

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query):
    stations = extract_stations(query)

    # ---------------- PROGRESS BAR ----------------
    progress = st.progress(0)
    status = st.empty()

    for i in range(100):
        progress.progress(i + 1)
        status.text(f"Analyzing query… {i + 1}%")
        time.sleep(0.01)

    progress.empty()
    status.empty()
    # ----------------------------------------------

    # No station detected
    if len(stations) == 0:
        place, nearby = find_nearby_location(query)

        if nearby:
            st.info(
                f"📍 **{place} is not a local train station.**\n\n"
                f"🚉 Nearest local stations: {', '.join(nearby)}\n\n"
                "You can take a local train till one of these stations "
                "and continue by taxi / bus / metro."
            )
            return

        st.warning(
            "I couldn’t identify valid stations.\n\n"
            "Example queries:\n"
            "- Virar to Churchgate\n"
            "- Panvel to CSMT"
        )
        return

    # Only one station found
    if len(stations) == 1:
        place, nearby = find_nearby_location(query)

        if nearby:
            st.info(
                f"📍 **{place} is not a local train station.**\n\n"
                f"🚉 Nearest local stations: {', '.join(nearby)}"
            )
            return

        st.warning(
            f"I found **{stations[0]}**, but couldn’t identify the destination.\n\n"
            "Please mention both source and destination."
        )
        return

    # Normal case
    src, dst = stations[0], stations[1]

    if src == dst:
        st.error("Source and destination cannot be the same.")
        return

    st.success(
        f"✅ **Route processed successfully**\n\n"
        f"From **{src}** → **{dst}**\n\n"
        "Local trains are available on this route."
    )

# --------------------------------------------------
# INPUT
# --------------------------------------------------

query = st.text_input(
    "Ask about routes, stations, or travel help",
    key="user_query",
    placeholder="e.g. Virar to Churchgate"
)

if query:
    chatbot_response(query)
