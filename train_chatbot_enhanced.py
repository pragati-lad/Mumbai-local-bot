# --------------------------------------------------
# MUMBAI LOCAL TRAIN CHATBOT (FULL + CENTRAL LINE)
# --------------------------------------------------

# ---------------- STATION DATA ----------------

WR_STATIONS = [
    "Churchgate","Marine Lines","Charni Road","Grant Road","Mumbai Central",
    "Mahalakshmi","Lower Parel","Prabhadevi","Dadar","Matunga Road",
    "Mahim Junction","Bandra","Khar Road","Santa Cruz","Vile Parle",
    "Andheri","Jogeshwari","Ram Mandir","Goregaon","Malad",
    "Kandivali","Borivali","Dahisar","Mira Road","Bhayandar",
    "Naigaon","Vasai Road","Nalla Sopara","Virar"
]

HARBOUR_STATIONS = [
    "Mumbai CSMT","Masjid","Sandhurst Road","Dockyard Road",
    "Sewri","Vadala Road","Kurla","Chembur","Govandi",
    "Mankhurd","Vashi","Sanpada","Belapur CBD","Panvel"
]

CENTRAL_STATIONS = [
    "Mumbai CSMT","Masjid","Sandhurst Road","Byculla","Chinchpokli",
    "Currey Road","Parel","Dadar","Matunga","Sion","Kurla",
    "Vidyavihar","Ghatkopar","Vikhroli","Kanjurmarg",
    "Bhandup","Nahur","Mulund","Thane","Kalwa","Mumbra",
    "Diva","Dombivli","Kalyan","Ulhasnagar","Badlapur","Karjat","Kasara"
]

ALL_STATIONS = list(set(WR_STATIONS + HARBOUR_STATIONS + CENTRAL_STATIONS))

# ---------------- TRAIN DATA (SAMPLE) ----------------

WR_TRAINS = {
    "UP": [
        {"train":"94002","virar":"04:00","borivali":"04:31","andheri":"04:51","bandra":"05:05","dadar":"05:14","churchgate":"05:36"},
    ],
    "DOWN": [
        {"train":"94001","churchgate":"05:40","dadar":"06:01","bandra":"06:11","andheri":"06:24","borivali":"06:45","virar":"07:52"},
    ],
}

HARBOUR_TRAINS = {
    "UP": [
        {"train":"98002","panvel":"04:03","vashi":"04:25","kurla":"04:44","mumbai csmt":"05:04"},
    ],
    "DOWN": [
        {"train":"98001","mumbai csmt":"00:13","kurla":"00:42","vashi":"01:02","panvel":"01:33"},
    ],
}

CENTRAL_TRAINS = {
    "UP": [
        {"train":"11001","kalyan":"06:00","thane":"06:35","kurla":"06:55","dadar":"07:05","mumbai csmt":"07:25"},
    ],
    "DOWN": [
        {"train":"11002","mumbai csmt":"18:00","dadar":"18:20","kurla":"18:30","thane":"18:55","kalyan":"19:30"},
    ],
}

# ---------------- NON-STATION LOCATIONS ----------------

NEARBY_LOCATIONS = {
    "malabar hills":["Charni Road","Grant Road"],
    "bkc":["Bandra","Kurla"],
    "bandra kurla complex":["Bandra","Kurla"],
    "powai":["Kanjurmarg"],
    "lower parel":["Lower Parel","Prabhadevi"],
    "andheri west":["Andheri"],
    "andheri east":["Andheri"],
}

# ---------------- HELPERS ----------------

def normalize(text):
    return text.lower().replace(" ", "").replace("-", "")

def find_stations(query):
    q = normalize(query)
    found = []
    for s in ALL_STATIONS:
        if normalize(s) in q:
            found.append(s)
    return list(dict.fromkeys(found))

def find_nearest_station_from_location(query):
    q = query.lower()
    for place, stations in NEARBY_LOCATIONS.items():
        if place in q:
            return place.title(), stations
    return None, None

def determine_line(src, dst):
    if src in CENTRAL_STATIONS or dst in CENTRAL_STATIONS:
        return "central"
    if src in HARBOUR_STATIONS or dst in HARBOUR_STATIONS:
        return "harbour"
    return "western"

def find_trains(src, dst, line):
    src_key, dst_key = normalize(src), normalize(dst)

    if line == "central":
        trains, stations = CENTRAL_TRAINS, CENTRAL_STATIONS
    elif line == "harbour":
        trains, stations = HARBOUR_TRAINS, HARBOUR_STATIONS
    else:
        trains, stations = WR_TRAINS, WR_STATIONS

    try:
        s_idx, d_idx = stations.index(src), stations.index(dst)
    except ValueError:
        return []

    direction = "UP" if s_idx < d_idx else "DOWN"

    results = []
    for t in trains[direction]:
        if src_key in t and dst_key in t:
            results.append(f"🚆 Train {t['train']} — {t[src_key]} → {t[dst_key]}")
    return results

# ---------------- CHATBOT CORE ----------------

def chatbot_response(user_input):
    stations = find_stations(user_input)

    # No station
    if len(stations) == 0:
        place, nearby = find_nearest_station_from_location(user_input)
        if nearby:
            return (
                f"📍 **{place} is not a local train station.**\n\n"
                "🚉 Nearest local stations:\n"
                + "\n".join(f"• {s}" for s in nearby) +
                "\n\nTake a local train till one of these stations and continue by taxi / bus / metro."
            )
        return "❌ I couldn’t identify any Mumbai local stations."

    # Only one station
    if len(stations) == 1:
        place, nearby = find_nearest_station_from_location(user_input)
        if nearby:
            return (
                f"📍 **{place} is not a local train station.**\n\n"
                "🚉 Nearest local stations:\n"
                + "\n".join(f"• {s}" for s in nearby)
            )
        return (
            f"⚠️ I found **{stations[0]}**, but couldn’t identify the destination.\n"
            "Please mention both source and destination."
        )

    # Normal flow
    src, dst = stations[0], stations[1]
    line = determine_line(src, dst)
    trains = find_trains(src, dst, line)

    if not trains:
        return (
            f"❌ No direct local trains found from **{src}** to **{dst}**.\n"
            "Try nearby stations or interchanges."
        )

    response = f"🚉 **Available {line.title()} line trains ({src} → {dst}):**\n\n"
    response += "\n".join(trains)
    return response
