# --------------------------------------------------
# MUMBAI LOCAL TRAIN CHATBOT (ENHANCED)
# --------------------------------------------------

# ---------------- STATION DATA ----------------

WR_STATIONS = [
    "Churchgate", "Marine Lines", "Charni Road", "Grant Road", "Mumbai Central",
    "Mahalakshmi", "Lower Parel", "Prabhadevi", "Dadar", "Matunga Road",
    "Mahim Junction", "Bandra", "Khar Road", "Santa Cruz", "Vile Parle",
    "Andheri", "Jogeshwari", "Ram Mandir", "Goregaon", "Malad",
    "Kandivali", "Borivali", "Dahisar", "Mira Road", "Bhayandar",
    "Naigaon", "Vasai Road", "Nalla Sopara", "Virar"
]

HARBOUR_STATIONS = [
    "Mumbai CSMT", "Masjid", "Sandhurst Road", "Dockyard Road",
    "Sewri", "Vadala Road", "Kurla", "Chembur",
    "Govandi", "Mankhurd", "Vashi", "Sanpada",
    "Belapur CBD", "Panvel"
]

ALL_STATIONS = WR_STATIONS + HARBOUR_STATIONS


# ---------------- TRAIN DATA (SAMPLE) ----------------

WR_TRAINS = {
    "UP": [
        {"train": "94002", "virar": "04:00", "borivali": "04:31", "andheri": "04:51", "bandra": "05:05", "dadar": "05:14", "churchgate": "05:36"},
        {"train": "94008", "virar": "07:15", "borivali": "07:53", "andheri": "08:15", "bandra": "08:24", "dadar": "08:30", "churchgate": "08:49"},
    ],
    "DOWN": [
        {"train": "94001", "churchgate": "05:40", "dadar": "06:01", "bandra": "06:11", "andheri": "06:24", "borivali": "06:45", "virar": "07:52"},
    ],
}

HARBOUR_TRAINS = {
    "UP": [
        {"train": "98002", "panvel": "04:03", "vashi": "04:25", "kurla": "04:44", "csmt": "05:04"},
        {"train": "98004", "panvel": "04:33", "vashi": "04:50", "kurla": "05:09", "csmt": "05:30"},
    ],
    "DOWN": [
        {"train": "98001", "csmt": "00:13", "kurla": "00:42", "vashi": "01:02", "panvel": "01:33"},
    ],
}


# --------------------------------------------------
# NEARBY LOCATION → STATION MAPPING
# --------------------------------------------------

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
    "lower parel": ["Prabhadevi", "Lower Parel"],
    "andheri west": ["Andheri"],
    "andheri east": ["Andheri"],
}


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text):
    return text.lower().replace(" ", "")

def find_stations(query):
    q = normalize(query)
    found = []

    for station in ALL_STATIONS:
        if normalize(station) in q or q in normalize(station):
            found.append(station)

    return list(dict.fromkeys(found))

def find_nearest_station_from_location(query):
    q = query.lower()
    for place, stations in NEARBY_LOCATIONS.items():
        if place in q:
            return place.title(), stations
    return None, None

def determine_line(src, dst):
    if src in HARBOUR_STATIONS or dst in HARBOUR_STATIONS:
        return "harbour"
    return "western"

def find_trains(src, dst, line):
    src_key = normalize(src)
    dst_key = normalize(dst)

    trains = HARBOUR_TRAINS if line == "harbour" else WR_TRAINS
    stations = HARBOUR_STATIONS if line == "harbour" else WR_STATIONS

    try:
        s_idx = stations.index(src)
        d_idx = stations.index(dst)
    except ValueError:
        return []

    direction = "UP" if s_idx < d_idx else "DOWN"

    results = []
    for t in trains[direction]:
        if src_key in t and dst_key in t:
            results.append(
                f"Train {t['train']} — {t[src_key]} → {t[dst_key]}"
            )
    return results


# --------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------

def chatbot_response(user_input):
    stations = find_stations(user_input)

    # Case 1: No station detected
    if len(stations) == 0:
        place, nearby = find_nearest_station_from_location(user_input)

        if nearby:
            return (
                f"📍 **{place} is not a local train station.**\n\n"
                "🚉 Nearest local stations:\n"
                + "\n".join([f"• {s}" for s in nearby]) +
                "\n\nYou can take a local train till one of these stations "
                "and then continue by taxi / bus / metro."
            )

        return (
            "❌ I couldn't identify any Mumbai local stations.\n\n"
            "Try examples like:\n"
            "- Virar to Churchgate\n"
            "- Panvel to CSMT\n"
            "- Andheri to Dadar"
        )

    # Case 2: Only one station detected
    if len(stations) == 1:
        place, nearby = find_nearest_station_from_location(user_input)

        if nearby:
            return (
                f"📍 **{place} is not a local train station.**\n\n"
                "🚉 Nearest local stations:\n"
                + "\n".join([f"• {s}" for s in nearby]) +
                "\n\nYou can take a local train till one of these stations "
                "and then continue by taxi / bus / metro."
            )

        return (
            f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination.\n\n"
            "Please mention a valid Mumbai local station or a known area."
        )

    # Case 3: Normal route
    src, dst = stations[0], stations[1]
    line = determine_line(src, dst)
    trains = find_trains(src, dst, line)

    if not trains:
        return (
            f"❌ No direct local trains found from **{src}** to **{dst}**.\n\n"
            "Try nearby stations or check the route."
        )

    response = f"🚆 **Available trains from {src} to {dst}:**\n\n"
    for t in trains:
        response += f"• {t}\n"

    return response
