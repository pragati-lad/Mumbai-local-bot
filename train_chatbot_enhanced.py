import streamlit as st
import time
from difflib import get_close_matches

# --------------------------------------------------
# DATA
# --------------------------------------------------

CENTRAL_STATIONS = [
    "CSMT","Masjid","Byculla","Chinchpokli","Currey Road",
    "Parel","Dadar","Matunga","Sion","Kurla","Vidyavihar",
    "Ghatkopar","Vikhroli","Kanjurmarg","Bhandup","Nahur",
    "Mulund","Thane","Kalyan"
]

WESTERN_STATIONS = [
    "Churchgate","Marine Lines","Charni Road","Grant Road",
    "Mumbai Central","Mahalakshmi","Lower Parel","Prabhadevi",
    "Dadar","Matunga Road","Mahim Junction","Bandra",
    "Khar Road","Santacruz","Vile Parle","Andheri",
    "Jogeshwari","Goregaon","Malad","Kandivali",
    "Borivali","Dahisar","Mira Road","Bhayandar",
    "Vasai Road","Nalla Sopara","Virar"
]

HARBOUR_STATIONS = [
    "CSMT","Masjid","Sandhurst Road","Dockyard Road","Sewri",
    "Vadala Road","Kurla","Chembur","Govandi","Mankhurd",
    "Vashi","Sanpada","Belapur CBD","Panvel"
]

ALL_STATIONS = list(set(CENTRAL_STATIONS + WESTERN_STATIONS + HARBOUR_STATIONS))

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
}

# --------------------------------------------------
# RULE TEXT (EXACT – NO VAGUE WORDS)
# --------------------------------------------------

LUGGAGE_RULES = """
🎒 **Luggage Rules in Mumbai Local Trains**

• **Second Class:** Up to **25 kg** allowed free  
• **First Class:** Up to **40 kg** allowed free  
• Oversized luggage must be **booked at the parcel office**  
• **Prohibited items:** inflammable materials, gas cylinders, explosives  

⚠️ Excess luggage may attract fines or removal from train  

**Source:** Indian Railways
"""

CONCESSION_RULES = """
🎟️ **Ticket Concessions (Mumbai Local)**

• **Students:** Up to 50% on season passes (with ID & bonafide)  
• **Senior Citizens:** 40% (Men 60+, Women 58+)  
• **Persons with Disabilities:** Up to 75% with certificate  

**Source:** Indian Railways
"""

REFUND_RULES = """
💰 **Refund Rules**

• Unused ticket: Refund before journey  
• Season ticket: Pro-rata refund (minimum 1 month unused)  
• Online tickets: Cancellation before departure  

**Source:** Indian Railways
"""

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

    if src_line == dst_line:
        return None, None, None

    if {"Central Line","Western Line"} == {src_line, dst_line}:
        return "Dadar", src_line, dst_line

    if {"Central Line","Harbour Line"} == {src_line, dst_line}:
        return "Kurla", src_line, dst_line

    return None, None, None

def is_timetable_query(q):
    return any(k in q for k in [
        "timetable","time table","schedule","timings",
        "western line","central line","harbour line"
    ])

# --------------------------------------------------
# CHATBOT CORE
# --------------------------------------------------

def chatbot_response(query):

    # fake processing bar (UX polish)
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.002)
    bar.empty()

    q = normalize(query)

    # ---- RULE INTENTS FIRST ----
    if "luggage" in q or "baggage" in q:
        return LUGGAGE_RULES

    if "concession" in q or "student" in q or "senior" in q:
        return CONCESSION_RULES

    if "refund" in q or "cancel" in q:
        return REFUND_RULES

    # ---- TIMETABLE ----
    if is_timetable_query(q):
        if "western" in q:
            return "**Western Line Timetable:** Churchgate ↔ Virar (3–5 min peak)"
        if "central" in q:
            return "**Central Line Timetable:** CSMT ↔ Kalyan (high frequency)"
        if "harbour" in q:
            return "**Harbour Line Timetable:** CSMT ↔ Panvel (10–15 min)"

    # ---- ROUTES ----
    stations = extract_stations(query)

    if len(stations) < 2:
        for place, near in NEARBY_LOCATIONS.items():
            if place in q:
                return (
                    f"📍 **{place.title()} is not a local train station.**\n\n"
                    f"🚉 Nearest stations: {', '.join(near)}\n\n"
                    "Take a local till one of these, then taxi/bus."
                )
        return (
            "❌ I couldn’t identify both stations.\n\n"
            "Try:\n• Dadar to Churchgate\n• Sion to Grant Road"
        )

    src, dst = stations[0], stations[1]

    interchange, src_line, dst_line = find_interchange(src, dst)

    if interchange:
        return f"""
🔁 **Route Information**

**From:** {src} ({src_line})  
**To:** {dst} ({dst_line})

🚉 **Change at:** {interchange}

**Steps:**
1. Travel on **{src_line}** till **{interchange}**
2. Change to **{dst_line}**
3. Continue to **{dst}**

⚠️ Platform numbers vary — check station boards.
"""

    # SAME LINE
    line = determine_line(src)
    return f"""
🚆 **Route Information**

**From:** {src}  
**To:** {dst}  

**Line:** {line}

• Direct local trains available  
• Platforms depend on direction  

⚠️ Check station display boards.
"""
