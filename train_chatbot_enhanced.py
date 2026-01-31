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

CENTRAL_STATIONS = [
    "CSMT", "Masjid", "Byculla", "Chinchpokli", "Currey Road",
    "Parel", "Dadar", "Matunga", "Sion", "Kurla",
    "Vidyavihar", "Ghatkopar", "Vikhroli", "Kanjurmarg",
    "Bhandup", "Nahur", "Mulund", "Thane", "Kalyan"
]

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

ALL_STATIONS = list(set(WESTERN_STATIONS + CENTRAL_STATIONS + HARBOUR_STATIONS))

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
}

# --------------------------------------------------
# UI HEADER
# --------------------------------------------------

st.title("Mumbai Local Train Assistant")
st.caption("Routes • Timetables • Platform Guidance")

st.markdown("### Suggested queries")
suggested = [
    "Sion to Grant Road",
    "Virar to Churchgate",
    "Panvel to CSMT",
    "Western line timetable"
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

def determine_line(station):
    if station in CENTRAL_STATIONS:
        return "Central Line"
    if station in HARBOUR_STATIONS:
        return "Harbour Line"
    return "Western Line"

def find_interchange(src, dst):
    src_line = determine_line(src)
    dst_line = determine_line(dst)

    if src_line != dst_line:
        if "Central" in (src_line, dst_line) and "Western" in (src_line, dst_line):
            return "Dadar", src_line, dst_line
        if "Central" in (src_line, dst_line) and "Harbour" in (src_line, dst_line):
            return "Kurla", src_line, dst_line
    return None, None, None

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query):

    # progress bar
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.002)
    bar.empty()

    stations = extract_stations(query)

    # No stations
    if len(stations) == 0:
        st.warning("Couldn’t identify Mumbai local stations.")
        return

    # One station
    if len(stations) == 1:
        st.warning(
            f"I found **{stations[0]}**, but couldn’t identify the destination.\n"
            "Please mention both source and destination."
        )
        return

    src, dst = stations[0], stations[1]

    # Interchange route
    interchange, src_line, dst_line = find_interchange(src, dst)
    if interchange:
        st.success("Route requires interchange")

        st.markdown(
            f"""
### 🔁 Route Details

**From:** {src}  
**Line:** {src_line}

➡️ **Travel till:** **{interchange}**

🔄 **Change from:**  
**{src_line} → {dst_line}**

➡️ Continue towards **{dst}**

⚠️ Platform numbers may change — check station boards.
"""
        )
        return

    # Same line route
    line = determine_line(src)

    st.success("Route processed successfully")

    st.markdown(
        f"""
### 🚆 Route Details

**From:** {src}  
**To:** {dst}

**Line:** {line}

• Direct local trains available  
• Platforms depend on direction  

⚠️ Check station display for exact platform number.
"""
    )

# --------------------------------------------------
# INPUT
# --------------------------------------------------

query = st.text_input(
    "Ask about routes, stations, or timetables",
    key="query",
    placeholder="e.g. Sion to Grant Road"
)

if query:
    chatbot_response(query)
