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

def station_line(station):
    if station in CENTRAL_STATIONS:
        return "Central Line"
    if station in HARBOUR_STATIONS:
        return "Harbour Line"
    return "Western Line"

def find_interchange(src_line, dst_line):
    if src_line == dst_line:
        return None
    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar"
    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla"
    return None

def is_rules_query(query):
    q = query.lower()
    return any(k in q for k in [
        "luggage", "concession", "refund", "cancel",
        "student", "senior", "rules", "allowance"
    ])

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query):

    # progress bar (UI only)
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.002)
    bar.empty()

    q = normalize(query)

    # ---------------- RULES INTENT ----------------
    if is_rules_query(query):

        if "luggage" in q:
            return (
                "🎒 **Luggage Allowance (Indian Railways)**\n\n"
                "• Free luggage depends on class\n"
                "• Excess luggage must be declared and paid\n"
                "• Oversized items go in the brake van\n\n"
                "Source: Indian Railways (CRIS)"
            )

        if "concession" in q:
            return (
                "🎟️ **Railway Concessions**\n\n"
                "• Students, senior citizens & disabled passengers eligible\n"
                "• Valid documents required\n"
                "• Concession varies by category\n\n"
                "Source: Indian Railways circulars"
            )

        if "refund" in q:
            return (
                "💰 **Ticket Refund Rules**\n\n"
                "• Depends on ticket type & cancellation time\n"
                "• Online tickets follow IRCTC policy\n"
                "• Deductions may apply\n\n"
                "Source: Indian Railways / IRCTC"
            )

    # ---------------- ROUTE LOGIC ----------------
    stations = extract_stations(query)

    if len(stations) == 0:
        for place, nearby in NEARBY_LOCATIONS.items():
            if place in q:
                return (
                    f"📍 **{place.title()} is not a local station**\n\n"
                    f"🚉 Nearest stations: {', '.join(nearby)}\n\n"
                    "Travel by local train till one of these, then continue by road."
                )

        return (
            "❌ I couldn’t identify Mumbai local stations.\n\n"
            "Try:\n• Dadar to Churchgate\n• Sion to Grant Road\n• Western line timetable"
        )

    if len(stations) == 1:
        return (
            f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination.\n"
            "Please mention both source and destination."
        )

    src, dst = stations[0], stations[1]
    src_line = station_line(src)
    dst_line = station_line(dst)

    # ---------------- SAME LINE ----------------
    if src_line == dst_line:
        return (
            f"🚆 **Route Information**\n\n"
            f"From: {src}\n"
            f"To: {dst}\n\n"
            f"Line: {src_line}\n\n"
            "• Direct local trains available\n"
            "• Platform depends on direction\n\n"
            "⚠️ Check station display boards."
        )

    # ---------------- INTERCHANGE ----------------
    interchange = find_interchange(src_line, dst_line)

    return (
        f"🔁 **Route Information**\n\n"
        f"From: {src} ({src_line})\n"
        f"To: {dst} ({dst_line})\n\n"
        f"🚉 Change at: **{interchange}**\n\n"
        "Steps:\n"
        f"1. Travel from **{src} → {interchange}** on **{src_line}**\n"
        f"2. Change to **{dst_line}** at **{interchange}**\n"
        f"3. Continue from **{interchange} → {dst}**\n\n"
        "⚠️ Platform numbers may vary. Check station boards."
    )
