import streamlit as st
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
    "powai": ["Kanjurmarg"]
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text):
    return text.lower().strip()

def fuzzy_match(word):
    matches = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.7)
    return matches[0] if matches else None

def extract_stations(query):
    found = []
    for word in query.split():
        m = fuzzy_match(word.title())
        if m and m not in found:
            found.append(m)
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
        return None, src_line, dst_line

    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar", src_line, dst_line

    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla", src_line, dst_line

    return None, src_line, dst_line

def is_rules_query(q):
    return any(x in q for x in [
        "luggage", "concession", "refund", "rules", "allowance"
    ])

def is_timetable_query(q):
    return any(x in q for x in [
        "timetable", "time table", "schedule", "timings",
        "western line", "central line", "harbour line"
    ])

# --------------------------------------------------
# MAIN LOGIC
# --------------------------------------------------

def chatbot_response(query: str) -> str:
    q = normalize(query)

    # ---------------- RULES (FIRST) ----------------
    if is_rules_query(q):
        if "luggage" in q:
            return (
                "🎒 **Luggage Rules in Mumbai Local Trains**\n\n"
                "• Free luggage allowed within prescribed size\n"
                "• Oversized luggage must be booked\n"
                "• No dangerous or inflammable items\n\n"
                "_Source: Indian Railways_"
            )

        if "concession" in q:
            return (
                "🎟️ **Railway Concession Rules**\n\n"
                "• Students, senior citizens & disabled passengers eligible\n"
                "• Valid documents required\n\n"
                "_Source: Indian Railways_"
            )

        if "refund" in q:
            return (
                "💰 **Ticket Refund Rules**\n\n"
                "• Depends on ticket type and timing\n"
                "• Online tickets follow IRCTC policy\n\n"
                "_Source: Indian Railways_"
            )

    # ---------------- TIMETABLE ----------------
    if is_timetable_query(q):
        if "western" in q:
            return (
                "🕒 **Western Line Timetable**\n\n"
                "Churchgate ↔ Virar\n"
                "• Peak: every 3–5 mins\n"
                "• Off-peak: every 5–8 mins"
            )

        if "central" in q:
            return (
                "🕒 **Central Line Timetable**\n\n"
                "CSMT ↔ Kalyan\n"
                "• High frequency throughout the day"
            )

        if "harbour" in q:
            return (
                "🕒 **Harbour Line Timetable**\n\n"
                "CSMT ↔ Panvel\n"
                "• Every 10–15 mins"
            )

    # ---------------- ROUTES ----------------
    stations = extract_stations(query)

    if len(stations) == 0:
        for place, nearby in NEARBY_LOCATIONS.items():
            if place in q:
                return (
                    f"📍 **{place.title()} is not a local station**\n\n"
                    f"🚉 Nearest stations: {', '.join(nearby)}"
                )

        return (
            "❌ I couldn’t identify Mumbai local stations.\n\n"
            "Try:\n• Dadar to Churchgate\n• Sion to Grant Road\n• Western line timetable"
        )

    if len(stations) == 1:
        return (
            f"⚠️ I found **{stations[0]}**, but not the destination.\n"
            "Please mention both source and destination."
        )

    src, dst = stations[0], stations[1]

    interchange, src_line, dst_line = find_interchange(src, dst)

    if interchange:
        return (
            "🔁 **Route Information**\n\n"
            f"From: {src} ({src_line})\n"
            f"To: {dst} ({dst_line})\n\n"
            f"🚉 Change at: **{interchange}**\n\n"
            f"1️⃣ Take a {src_line} local from **{src} → {interchange}**\n"
            f"2️⃣ Change to **{dst_line}**\n"
            f"3️⃣ Continue **{interchange} → {dst}**\n\n"
            "⚠️ Platform numbers may vary."
        )

    return (
        "🚆 **Route Information**\n\n"
        f"From: {src}\n"
        f"To: {dst}\n\n"
        f"Line: {src_line}\n"
        "• Direct local trains available\n"
        "• Platform depends on direction\n\n"
        "⚠️ Check station display boards."
    )
