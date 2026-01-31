import streamlit as st
import time
from difflib import get_close_matches

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
    "Churchgate", "Marine Lines", "Charni Road", "Grant Road",
    "Mumbai Central", "Mahalakshmi", "Lower Parel", "Prabhadevi",
    "Dadar", "Matunga Road", "Mahim Junction", "Bandra",
    "Khar Road", "Santacruz", "Vile Parle", "Andheri",
    "Jogeshwari", "Goregaon", "Malad", "Kandivali",
    "Borivali", "Dahisar", "Mira Road", "Bhayandar",
    "Vasai Road", "Nalla Sopara", "Virar"
]

HARBOUR_STATIONS = [
    "CSMT", "Masjid", "Sandhurst Road", "Dockyard Road",
    "Sewri", "Vadala Road", "Kurla", "Chembur",
    "Govandi", "Mankhurd", "Vashi", "Sanpada",
    "Belapur CBD", "Panvel"
]

ALL_STATIONS = list(set(CENTRAL_STATIONS + WESTERN_STATIONS + HARBOUR_STATIONS))

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text: str) -> str:
    return text.lower().strip()

def fuzzy_match(word: str):
    matches = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.65)
    return matches[0] if matches else None

def extract_stations(query: str):
    """
    Preserve station order exactly as user typed.
    """
    q = normalize(query)
    matches = []

    for station in ALL_STATIONS:
        pos = q.find(normalize(station))
        if pos != -1:
            matches.append((pos, station))

    matches.sort(key=lambda x: x[0])
    stations = [s for _, s in matches]

    # fallback fuzzy match
    if len(stations) < 2:
        for word in query.split():
            match = fuzzy_match(word.title())
            if match and match not in stations:
                stations.append(match)

    return stations[:2]

def determine_line(station: str) -> str:
    if station in CENTRAL_STATIONS:
        return "Central Line"
    if station in HARBOUR_STATIONS:
        return "Harbour Line"
    return "Western Line"

def find_interchange(src: str, dst: str):
    src_line = determine_line(src)
    dst_line = determine_line(dst)

    if src_line == dst_line:
        return None, src_line, dst_line

    # Common Mumbai interchanges
    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar", src_line, dst_line

    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla", src_line, dst_line

    if {"Western Line", "Harbour Line"} == {src_line, dst_line}:
        return "Mumbai Central / Dadar", src_line, dst_line

    return None, src_line, dst_line

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query: str):

    # progress bar
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.002)
    bar.empty()

    stations = extract_stations(query)

    # -------- NO STATION --------
    if len(stations) == 0:
        for place, nearby in NEARBY_LOCATIONS.items():
            if place in normalize(query):
                return (
                    f"📍 **{place.title()} is not a local train station.**\n\n"
                    f"🚉 Nearest stations: {', '.join(nearby)}\n\n"
                    "You can take a local train till one of these stations and continue by taxi / bus / metro."
                )

        return (
            "❌ I couldn’t identify Mumbai local stations.\n\n"
            "Try examples like:\n"
            "• Sion to Grant Road\n"
            "• Virar to Churchgate\n"
            "• Panvel to CSMT"
        )

    # -------- ONE STATION --------
    if len(stations) == 1:
        return (
            f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination.\n"
            "Please mention both source and destination."
        )

    src, dst = stations[0], stations[1]

    if src == dst:
        return "⚠️ Source and destination cannot be the same."

    interchange, src_line, dst_line = find_interchange(src, dst)

    # -------- INTERCHANGE ROUTE --------
    if interchange:
        return f"""
### 🔁 Route Information

**From:** {src} ({src_line})  
**To:** {dst} ({dst_line})

🚉 **Change at:** **{interchange}**

**Steps:**
1. Take a **{src_line} local** from **{src} → {interchange}**
2. Change to **{dst_line}**
3. Continue from **{interchange} → {dst}**

⚠️ Platform numbers may vary. Check station display boards.
"""

    # -------- DIRECT ROUTE --------
    return f"""
### 🚆 Route Information

**From:** {src}  
**To:** {dst}

**Line:** {src_line}

• Direct local trains available  
• Platforms depend on direction  

⚠️ Check station display boards for exact platform number.
"""
