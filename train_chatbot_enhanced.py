# ==================================================
# Mumbai Local Train Assistant – Core Logic (FIXED)
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
# RULES (SEPARATED PROPERLY)
# --------------------------------------------------

STUDENT_CONCESSION = """
🎓 **Student Concession – Mumbai Local Trains**

Eligible for **Monthly / Quarterly Season Pass** at concessional rates.

📄 **Documents Required:**
• Bonafide certificate from school/college  
• Valid ID card  
• Filled railway concession form  
• Recent passport-size photo  

📍 Issued at suburban ticket counters only  
⚠️ Not applicable on single journey tickets  

_Source: Indian Railways_
"""

SENIOR_CONCESSION = """
👴 **Senior Citizen Concession**

• Men: 60+ years → 40% concession  
• Women: 58+ years → 50% concession  

Valid on:
• Single journey tickets  
• Season tickets  

_Source: Indian Railways_
"""

DISABILITY_CONCESSION = """
♿ **Concession for Persons with Disabilities**

• Up to **75% concession**  
• Applicable for season & single journey tickets  

📄 Disability certificate required  

_Source: Indian Railways_
"""

GENERAL_CONCESSION = """
🎟️ **Railway Concessions (Summary)**

• Students – Monthly / Quarterly pass  
• Senior citizens – 40–50%  
• Persons with disabilities – Up to 75%  

Ask specifically for:
• Student concession  
• Senior citizen concession  
• Disability concession
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

    # ---------- CONCESSION INTENT (FIXED) ----------
    if "student" in q:
        return STUDENT_CONCESSION

    if "senior" in q:
        return SENIOR_CONCESSION

    if "disable" in q or "disability" in q:
        return DISABILITY_CONCESSION

    if "concession" in q:
        return GENERAL_CONCESSION

    # ---------- ROUTE ----------
    stations = extract_stations(query)

    if len(stations) < 2:
        return (
            "❌ I couldn’t identify both source and destination.\n\n"
            "Try:\n• Sion to Grant Road\n• Dadar to Churchgate\n• Student concession documents"
        )

    src, dst = stations[0], stations[1]
    src_line = determine_line(src)
    dst_line = determine_line(dst)

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

    return f"""
🚆 **Route Information**

From: {src}  
To: {dst}  

Line: {src_line}

• Direct local trains available  
• Frequency depends on time of day  

⚠️ Check station display boards for platform numbers.
"""
