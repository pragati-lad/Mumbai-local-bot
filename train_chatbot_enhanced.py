from difflib import get_close_matches

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


def normalize(text):
    return text.lower().strip()


def fuzzy_match(word):
    matches = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.65)
    return matches[0] if matches else None


def extract_stations(query):
    q = normalize(query)
    found = []

    for station in ALL_STATIONS:
        if normalize(station) in q:
            found.append(station)

    if len(found) < 2:
        for word in query.split():
            match = fuzzy_match(word.title())
            if match and match not in found:
                found.append(match)

    return found[:2]


def get_line(station):
    if station in CENTRAL_STATIONS:
        return "Central Line"
    if station in HARBOUR_STATIONS:
        return "Harbour Line"
    return "Western Line"


def find_interchange(src_line, dst_line):
    if src_line != dst_line:
        if "Central Line" in (src_line, dst_line) and "Western Line" in (src_line, dst_line):
            return "Dadar"
        if "Central Line" in (src_line, dst_line) and "Harbour Line" in (src_line, dst_line):
            return "Kurla"
    return None


def chatbot_response(query: str) -> str:
    stations = extract_stations(query)

    if len(stations) == 0:
        return "❌ I couldn’t identify any Mumbai local stations."

    if len(stations) == 1:
        return f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination."

    src, dst = stations
    if src == dst:
        return "⚠️ Source and destination cannot be the same."

    src_line = get_line(src)
    dst_line = get_line(dst)

    if src_line != dst_line:
        interchange = find_interchange(src_line, dst_line)
        return (
            f"### 🔁 Route Information\n\n"
            f"**From:** {src} ({src_line})\n"
            f"**To:** {dst} ({dst_line})\n\n"
            f"🚉 **Change at:** **{interchange}**\n\n"
            f"1. Take a **{src_line} local** from **{src} → {interchange}**\n"
            f"2. Change to **{dst_line}** at **{interchange}**\n"
            f"3. Continue from **{interchange} → {dst}**\n\n"
            f"⚠️ Platform numbers may vary. Check station display boards."
        )

    return (
        f"### 🚆 Route Information\n\n"
        f"**From:** {src}\n"
        f"**To:** {dst}\n\n"
        f"**Line:** {src_line}\n\n"
        f"• Direct local trains available\n"
        f"⚠️ Check station display boards for platform information."
    )
