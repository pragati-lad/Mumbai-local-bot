import re
from datetime import datetime

# ================= TRAIN DATA =================

WR_AC_TRAINS = {
    "UP": [
        {"train": "94002", "type": "AC", "virar": "04:00", "borivali": "04:31", "andheri": "04:51", "bandra": "05:05", "dadar": "05:14", "churchgate": "05:36"},
        {"train": "94006", "type": "AC", "nalla_sopara": "06:03", "borivali": "06:36", "andheri": "06:58", "bandra": "07:06", "dadar": "07:13", "churchgate": "07:32"},
        {"train": "94008", "type": "AC", "virar": "07:15", "borivali": "07:53", "andheri": "08:15", "bandra": "08:24", "dadar": "08:30", "churchgate": "08:49"},
    ],
    "DOWN": [
        {"train": "94001", "type": "AC", "churchgate": "05:40", "dadar": "06:01", "bandra": "06:11", "andheri": "06:24", "borivali": "06:45", "virar": "07:52"},
    ]
}

HARBOUR_TRAINS = {
    "UP": [
        {"train": "98002", "panvel": "04:03", "vashi": "04:25", "kurla": "04:44", "dadar": "04:54", "csmt": "05:04"},
    ],
    "DOWN": [
        {"train": "98001", "csmt": "00:13", "dadar": "00:31", "kurla": "00:42", "vashi": "01:02", "panvel": "01:33"},
    ]
}

WR_STATIONS = ["Virar", "Borivali", "Andheri", "Bandra", "Dadar", "Churchgate"]
HARBOUR_STATIONS = ["Panvel", "Vashi", "Kurla", "Dadar", "CSMT"]

RAILWAY_RULES = {
    "student": "Students get 25% concession on passes.",
    "senior": "Senior citizens get 40% concession.",
    "luggage": "Free luggage allowed up to 40kg in AC.",
    "refund": "Unused tickets can be refunded before journey."
}

# ================= HELPERS =================

def parse_time(t):
    try:
        return datetime.strptime(t, "%H:%M")
    except:
        return None

def find_station(query, stations):
    return [s for s in stations if s.lower() in query.lower()]

def find_trains(from_s, to_s, data):
    result = []
    for direction in data:
        for train in data[direction]:
            if from_s in train and to_s in train:
                result.append(train)
    return result

# ================= MAIN LOGIC =================

def chatbot_response(user_input: str) -> str:
    q = user_input.lower()

    # Rules
    for key in RAILWAY_RULES:
        if key in q:
            return f"📋 **Rule:** {RAILWAY_RULES[key]}"

    # Detect line
    line = "harbour" if any(x in q for x in ["panvel", "csmt", "vashi"]) else "western"

    stations = HARBOUR_STATIONS if line == "harbour" else WR_STATIONS
    trains = HARBOUR_TRAINS if line == "harbour" else WR_AC_TRAINS

    found = find_station(q, stations)

    if len(found) < 2:
        return "❓ Please mention both source and destination stations."

    from_s, to_s = found[0].lower(), found[1].lower()

    results = find_trains(from_s, to_s, trains)

    if not results:
        return "❌ No trains found."

    response = "🚆 **Available Trains:**\n\n"
    for t in results:
        response += f"• Train {t['train']} ({t.get('type','Regular')})\n"

    return response
