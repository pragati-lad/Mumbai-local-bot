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

ALL_STATIONS = list(set(WESTERN_STATIONS + CENTRAL_STATIONS + HARBOUR_STATIONS))

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

    # Central ↔ Western
    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar", src_line, dst_line

    # Central ↔ Harbour
    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla", src_line, dst_line

    return None, None, None

# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(query):

    # Progress bar (visual only)
    bar = st.progress(0)
    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.002)
    bar.empty()

    stations = extract_stations(query)

    # No stations
    if len(stations) == 0:
        return (
            "❌ I couldn’t identify Mumbai local stations.\n\n"
            "Try examples like:\n"
            "• Dadar to Churchgate\n"
            "• Sion to Grant Road\n"
            "• Western line timetable"
        )

    # One station
    if len(stations) == 1:
        return (
            f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination.\n\n"
            "Please mention both source and destination."
        )

    # Preserve user order
    src, dst = stations[0], stations[1]

    if src == dst:
        return "⚠️ Source and destination cannot be the same."

    src_line = determine_line(src)
    dst_line = determine_line(dst)

    interchange, _, _ = find_interchange(src, dst)

    # --------------------------------------------------
    # INTERCHANGE ROUTE (FIXED LOGIC)
    # --------------------------------------------------
    if interchange:

        steps = []

        # Case 1: Source IS the interchange
        if src == interchange:
            steps.append(
                f"• You are already at **{interchange}**.\n"
                f"• Move to the **{dst_line}** platforms."
            )

        # Case 2: Destination IS the interchange
        elif dst == interchange:
            steps.append(
                f"• Take a **{src_line}** local from **{src} → {interchange}**."
            )

        # Case 3: Normal interchange travel
        else:
            steps.append(
                f"• Take a **{src_line}** local from **{src} → {interchange}**."
            )
            steps.append(
                f"• Change from **{src_line} → {dst_line}** at **{interchange}**."
            )

        # Continue after interchange (only if needed)
        if dst != interchange:
            steps.append(
                f"• Continue on **{dst_line}** from **{interchange} → {dst}**."
            )

        steps_text = "\n".join(steps)

        return (
            "🔁 **Route Information**\n\n"
            f"**From:** {src} ({src_line})\n"
            f"**To:** {dst} ({dst_line})\n\n"
            f"🚉 **Interchange at:** {interchange}\n\n"
            f"**Steps:**\n{steps_text}\n\n"
            "⚠️ Platform numbers may vary. Check station display boards."
        )

    # --------------------------------------------------
    # SAME LINE ROUTE
    # --------------------------------------------------
    return (
        "🚆 **Route Information**\n\n"
        f"**From:** {src}\n"
        f"**To:** {dst}\n\n"
        f"**Line:** {src_line}\n\n"
        "• Direct local trains available\n"
        "• Fast / Slow depends on time of day\n\n"
        "⚠️ Platform numbers may vary. Check station display boards."
    )
