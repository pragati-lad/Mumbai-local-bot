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

WESTERN_STATIONS = [
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

ALL_STATIONS = WESTERN_STATIONS + HARBOUR_STATIONS

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
st.caption("Routes • Timetables • Platform Guidance")

st.markdown("### Suggested queries")
suggested = [
    "Virar to Churchgate",
    "Prabhadevi to Dadar",
    "Panvel to CSMT",
    "Western line timetable",
    "Virar to Malabar Hills"
]

cols = st.columns(2)
for i, q in enumerate(suggested):
    if cols[i % 2].button(q):
        st.session_state.query = q

st.divider()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text):
    return text.lower().strip()

def fuzzy_match(word):
    matches = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.65)
    return matches[0] if matches else None

def extract_stations(query):
    found = []
    for word in query.split():
        match = fuzzy_match(word.title())
        if match and match not in found:
            found.append(match)
    return found

def find_nearby_location(query):
    q = normalize(query)
    for place, stations in NEARBY_LOCATIONS.items():
        if place in q:
            return place.title(), stations
    return None, None

def determine_line(src, dst):
    if src in HARBOUR_STATIONS or dst in HARBOUR_STATIONS:
        return "Harbour Line"
    return "Western Line"

def determine_direction(line, src, dst):
    stations = HARBOUR_STATIONS if line == "Harbour Line" else WESTERN_STATIONS
    return "Up (towards city)" if stations.index(src) < stations.index(dst) else "Down (outbound)"

def determine_platform(line, direction):
    if line == "Western Line":
        return "Usually Platform 1–2 (Up) or 3–4 (Down)"
    return "Harbour Line platforms vary by station"

def train_type(src, dst):
    if src in WESTERN_STATIONS and dst in WESTERN_STATIONS:
        distance = abs(WESTERN_STATIONS.index(src) - WESTERN_STATIONS.index(dst))
        return "Fast or Slow" if distance > 6 else "Slow"
    return "Regular Harbour Local"

def is_timetable_query(query):
    q = normalize(query)
    keywords = [
        "timetable", "time table", "time tale", "timings", "schedule",
        "western line", "harbour line", "central line"
    ]
    return any(k in q for k in keywords)

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query):

    # ---------------- Progress bar ----------------
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.004)
    bar.empty()
    # ---------------------------------------------

    q = normalize(query)

    # -------- TIMETABLE INTENT (FIRST) ------------
    if is_timetable_query(query):

        if "western" in q:
            st.success("Western Line Timetable")
            st.markdown(
                """
**Route:** Churchgate ↔ Virar  

• Slow & fast locals  
• Peak hours: every 3–5 minutes  
• Off-peak: every 5–8 minutes  

📍 Platforms depend on direction  
⚠️ Check station display boards for live updates
"""
            )
            return

        if "harbour" in q:
            st.success("Harbour Line Timetable")
            st.markdown(
                """
**Route:** CSMT ↔ Panvel  

• Regular harbour locals  
• Frequency: every 10–15 minutes  

📍 Platforms vary by station
"""
            )
            return

        if "central" in q:
            st.success("Central Line Timetable")
            st.markdown(
                """
**Route:** CSMT ↔ Kasara / Karjat  

• Slow & fast locals  
• Very high peak-hour frequency  

📍 Platforms depend on destination
"""
            )
            return
    # ---------------------------------------------

    stations = extract_stations(query)

    # No stations
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
            "I couldn’t identify Mumbai local stations.\n\n"
            "Try:\n• Virar to Churchgate\n• Western line timetable"
        )
        return

    # One station
    if len(stations) == 1:
        st.warning(
            f"I found **{stations[0]}**, but couldn’t identify the destination.\n"
            "Please mention both source and destination."
        )
        return

    # Normal route case
    src, dst = stations[0], stations[1]
    if src == dst:
        st.error("Source and destination cannot be the same.")
        return

    line = determine_line(src, dst)
    direction = determine_direction(line, src, dst)
    platform = determine_platform(line, direction)
    ttype = train_type(src, dst)

    st.success("Route processed successfully")

    st.markdown(
        f"""
### 🚆 Route Details

**From:** {src}  
**To:** {dst}  

**Line:** {line}  
**Direction:** {direction}  
**Train Type:** {ttype}  

**Platform Info:**  
• {platform}

⏱️ **Frequency:**  
• Peak: 3–5 minutes  
• Off-peak: 5–8 minutes  

⚠️ *Platform numbers are indicative and may change.*
"""
    )

# --------------------------------------------------
# INPUT
# --------------------------------------------------

query = st.text_input(
    "Ask about routes, stations, or timetables",
    key="query",
    placeholder="e.g. Western line timetable"
)

if query:
    chatbot_response(query)
