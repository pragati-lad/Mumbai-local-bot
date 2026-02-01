# ==================================================
# Mumbai Local Train Assistant – Core Logic (FINAL)
# ==================================================

from difflib import get_close_matches

# ---------------- STATION DATA ----------------

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

# ---------------- INFORMATION ----------------

STUDENT_CONCESSION = """
🎓 **Student Concession – Mumbai Local Trains**

• Applicable on Monthly / Quarterly passes  
• Bonafide certificate + student ID required  
• Issued at suburban ticket counters only  

⚠️ Not valid for single-journey tickets
"""

SENIOR_CONCESSION = """
👴 **Senior Citizen Concession**

• Men: 60+ years → 40%  
• Women: 58+ years → 50%  

Valid on tickets & passes
"""

LUGGAGE_RULES = """
🎒 **Luggage Rules**

• Second Class: up to 15 kg  
• First Class: up to 20 kg  
• Size limit: 100 × 60 × 25 cm  

Oversized luggage must be booked separately
"""

MONTHLY_PASS = """
🎟️ **Monthly / Quarterly Pass**

• First & Second Class available  
• Concessions applicable  
• Price depends on distance
"""

# ---------------- HELPERS ----------------

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

def find_interchange(src_line, dst_line):
    if src_line == dst_line:
        return None
    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar"
    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla"
    return None

# ---------------- CHATBOT RESPONSE ----------------

def chatbot_response(query: str):

    q = normalize(query)

    # ---- INFO INTENTS FIRST ----
    if "student" in q:
        return STUDENT_CONCESSION

    if "senior" in q:
        return SENIOR_CONCESSION

    if "luggage" in q:
        return LUGGAGE_RULES

    if "monthly" in q or "quarterly" in q or "pass" in q:
        return MONTHLY_PASS

    # ---- ROUTE LOGIC ----
    stations = extract_stations(query)

    if len(stations) < 2:
        return (
            "❌ I couldn’t identify both source and destination.\n\n"
            "Try:\n• Sion to Grant Road\n• Dadar to Churchgate\n• Student concession"
        )

    src, dst = stations[0], stations[1]

    if src == dst:
        return "⚠️ Source and destination cannot be the same."

    src_line = determine_line(src)
    dst_line = determine_line(dst)

    interchange = find_interchange(src_line, dst_line)

    if interchange:
        return f"""
🔁 **Route Information**

From: **{src}** ({src_line})  
To: **{dst}** ({dst_line})

🚉 Change at **{interchange}**

1. {src} → {interchange} ({src_line})
2. Switch to {dst_line}
3. {interchange} → {dst}
"""

    return f"""
🚆 **Route Information**

From: **{src}**  
To: **{dst}**

Line: **{src_line}**

• Direct locals available  
• Platform depends on direction
"""
