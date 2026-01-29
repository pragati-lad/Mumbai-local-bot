import re
from datetime import datetime

# ---------------- DATA ----------------

WR_AC_TRAINS = {
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


# ---------------- HELPERS ----------------

def normalize(text):
    return text.lower().replace(" ", "")

def find_stations_in_query(query):
    q = normalize(query)
    found = []

    for station in ALL_STATIONS:
        if normalize(station) in q or q in normalize(station):
            found.append(station)

    return list(dict.fromkeys(found))


def determine_line(from_station, to_station):
    if from_station in HARBOUR_STATIONS or to_station in HARBOUR_STATIONS:
        return "harbour"
    return "western"


def find_trains(from_station, to_station, line):
    from_key = normalize(from_station)
    to_key = normalize(to_station)

    data = HARBOUR_TRAINS if line == "harbour" else WR_AC_TRAINS
    stations = HARBOUR_STATIONS if line == "harbour" else WR_STATIONS

    try:
        from_idx = stations.index(from_station)
        to_idx = stations.index(to_station)
    except ValueError:
        return []

    direction = "UP" if from_idx < to_idx else "DOWN"

    results = []
    for train in data[direction]:
        if from_key in train and to_key in train:
            results.append(
                f"Train {train['train']} — Departs {train[from_key]} → Arrives {train[to_key]}"
            )

    return results


# ---------------- MAIN CHATBOT ----------------

def chatbot_response(user_input):
    stations = find_stations_in_query(user_input)

    if len(stations) == 0:
        return (
            "❌ I couldn't identify any Mumbai local stations.\n\n"
            "**Try examples like:**\n"
            "- Virar to Churchgate\n"
            "- Panvel to CSMT"
        )

    if len(stations) == 1:
        return (
            f"⚠️ I found **{stations[0]}**, but I couldn’t identify the other station.\n\n"
            "Please enter both **source and destination** as valid Mumbai local stations."
        )

    from_station, to_station = stations[0], stations[1]
    line = determine_line(from_station, to_station)

    trains = find_trains(from_station, to_station, line)

    if not trains:
        return (
            f"❌ No direct local trains found from **{from_station}** to **{to_station}**.\n\n"
            "Please check the route or try nearby stations."
        )

    response = f"🚆 **Available trains from {from_station} to {to_station}:**\n\n"
    for t in trains:
        response += f"• {t}\n"

    return response
