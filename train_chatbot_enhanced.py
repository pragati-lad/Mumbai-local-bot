# ==================================================
# Mumbai Local Train Assistant – Core Logic
# ==================================================

from difflib import get_close_matches

# --------------------------------------------------
# STATION DATA
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
    "Dadar", "Mahim Junction", "Bandra", "Khar Road",
    "Santacruz", "Vile Parle", "Andheri", "Jogeshwari",
    "Goregaon", "Malad", "Kandivali", "Borivali",
    "Dahisar", "Mira Road", "Bhayandar",
    "Vasai Road", "Nalla Sopara", "Virar"
]

HARBOUR_STATIONS = [
    "CSMT", "Masjid", "Sandhurst Road", "Dockyard Road",
    "Sewri", "Vadala Road", "Kurla", "Chembur",
    "Govandi", "Mankhurd", "Vashi", "Sanpada",
    "Belapur CBD", "Panvel"
]

ALL_STATIONS = list(set(CENTRAL_STATIONS + WESTERN_STATIONS + HARBOUR_STATIONS))

# --------------------------------------------------
# NEARBY LOCATIONS (NON-STATION AREAS)
# --------------------------------------------------

NEARBY_LOCATIONS = {
    "malabar hills": ["Charni Road", "Grant Road"],
    "bkc": ["Bandra", "Kurla"],
    "bandra kurla complex": ["Bandra", "Kurla"],
    "powai": ["Kanjurmarg"],
}

# --------------------------------------------------
# AC TRAIN INFORMATION (HONEST DATA)
# --------------------------------------------------

AC_TRAIN_INFO = {
    "Western Line": {
        "route": "Churchgate ↔ Virar",
        "availability": "Available on selected services",
        "frequency": "Every 20–30 minutes (peak)",
        "fare": "Approx. 1.3× First Class fare",
        "notes": [
            "Limited stops",
            "UTS / smart card supported",
            "Platform varies by station"
        ]
    },
    "Central Line": {
        "route": "CSMT ↔ Kalyan",
        "availability": "Available on selected services",
        "frequency": "Every 30–40 minutes",
        "fare": "Approx. 1.3× First Class fare",
        "notes": [
            "High peak-hour demand",
            "Check station boards for timings"
        ]
    },
    "Harbour Line": {
        "route": "CSMT ↔ Panvel",
        "availability": "Very limited services",
        "frequency": "Few trains per day",
        "fare": "Approx. 1.3× First Class fare",
        "notes": [
            "Pilot basis",
            "Subject to change"
        ]
    }
}

# --------------------------------------------------
# RULES DATA (FROM OFFICIAL PDFs)
# --------------------------------------------------

LUGGAGE_RULES = """
🎒 **Luggage Rules in Mumbai Local Trains**

• Free luggage allowed up to **25 kg** (Second class)  
• Up to **40 kg** in First Class  
• Oversized luggage must be booked separately  
• No inflammable or dangerous items allowed  

_Source: Indian Railways_
"""

CONCESSION_RULES = """
🎟️ **Railway Concessions**

• Students: Monthly / Quarterly pass concession  
• Senior citizens: 40%–50% depending on age  
• Persons with disabilities: Up to 75%  

_Source: Indian Railways_
"""

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize(text):
    return text.lower().strip()

def fuzzy_station(word):
    match = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.65)
    return match[0] if match else None

def extract_stations(query):
    found = []
    for w in query.split():
        s = fuzzy_station(w.title())
        if s and s not in found:
            found.append(s)
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
        return None

    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar"

    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla"

    return None

# --------------------------------------------------
# CHATBOT RESPONSE
# --------------------------------------------------

def chatbot_response(query: str):

    q = normalize(query)

    # ---------- RULE QUERIES ----------
    if "luggage" in q:
        return LUGGAGE_RULES

    if "concession" in q or "student" in q or "senior" in q:
        return CONCESSION_RULES

    # ---------- AC TRAIN QUERIES ----------
    if "ac" in q:
        if "western" in q:
            info = AC_TRAIN_INFO["Western Line"]
        elif "central" in q:
            info = AC_TRAIN_INFO["Central Line"]
        elif "harbour" in q:
            info = AC_TRAIN_INFO["Harbour Line"]
        else:
            return (
                "🚆 **AC locals are available on Western, Central and Harbour lines.**\n\n"
                "Try:\n• AC trains on Western line\n• AC trains on Central line"
            )

        notes = "\n".join([f"• {n}" for n in info["notes"]])
        return f"""
🚆 **AC Local Trains – {info['route']}**

Availability: {info['availability']}  
Frequency: {info['frequency']}  
Fare: {info['fare']}  

📌 Notes:
{notes}
"""

    # ---------- LOCATION (NON-STATION) ----------
    for place, nearby in NEARBY_LOCATIONS.items():
        if place in q:
            return (
                f"📍 **{place.title()} is not a local train station.**\n\n"
                f"Nearest local stations:\n• " + " • ".join(nearby) +
                "\n\nTake a local train till one of these and continue by taxi / bus."
            )

    # ---------- ROUTE QUERIES ----------
    stations = extract_stations(query)

    if len(stations) < 2:
        return (
            "❌ I couldn’t identify both source and destination.\n\n"
            "Try:\n• Sion to Grant Road\n• Dadar to Churchgate\n• Western line timetable"
        )

    src, dst = stations[0], stations[1]
    src_line = determine_line(src)
    dst_line = determine_line(dst)

    # ---------- INTERCHANGE REQUIRED ----------
    interchange = find_interchange(src, dst)
    if interchange:
        return f"""
🔁 **Route Information**

From: {src} ({src_line})  
To: {dst} ({dst_line})  

🚉 **Change at:** {interchange}

Steps:
1. Take a {src_line} local from **{src} → {interchange}**
2. Change to **{dst_line}**
3. Continue from **{interchange} → {dst}**

⚠️ Platform numbers depend on station boards.
"""

    # ---------- SAME LINE ----------
    return f"""
🚆 **Route Information**

From: {src}  
To: {dst}  

Line: {src_line}

• Direct local trains available  
• Frequency depends on time of day  

⚠️ Check station display boards for platform numbers.
"""
