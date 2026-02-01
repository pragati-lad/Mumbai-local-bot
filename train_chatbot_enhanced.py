# ==================================================
# Mumbai Local Train Assistant – Core Logic (FINAL)
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
# INFORMATION / RULES
# --------------------------------------------------

STUDENT_CONCESSION = """
🎓 **Student Concession – Mumbai Local Trains**

Eligible for **Monthly / Quarterly Season Pass** at concessional rates.

📄 **Documents Required**
• Bonafide certificate from school / college  
• Valid student ID card  
• Filled railway concession form  
• Passport-size photograph  

⚠️ Not valid for single-journey tickets  
📍 Issued at suburban ticket counters only  

_Source: Indian Railways_
"""

SENIOR_CITIZEN = """
👴 **Senior Citizen Concession – Mumbai Local Trains**

• Applicable for passengers aged **60 years & above**
• Valid government photo ID required
• Concession available on **Monthly & Quarterly passes**
• Discount varies by distance & class

📍 Issued at suburban ticket counters only  

_Source: Indian Railways_
"""

MONTHLY_PASS = """
🎟️ **Monthly / Quarterly Pass Rules**

• Available for **First & Second Class**
• Student & Senior Citizen concession applicable
• Valid between selected source & destination only
• No refund after pass activation

💰 **Approximate Pass Fees (Distance-based)**

Second Class:
• Monthly: ₹100 – ₹300
• Quarterly: ₹300 – ₹900

First Class:
• Monthly: ₹400 – ₹1200
• Quarterly: ₹1200 – ₹3600

_Source: Indian Railways_
"""

LUGGAGE_RULES = """
🎒 **Luggage Rules – Mumbai Local Trains**

✅ **Free allowance**
• Up to **15 kg** in Second Class  
• Up to **20 kg** in First Class  

📦 **Size limit**
• Max: **100 cm × 60 cm × 25 cm**

❌ Dangerous / inflammable items not allowed  
📍 Oversized luggage must be booked separately  

_Source: Indian Railways_
"""

AC_TRAINS = """
❄️ **AC Local Trains (Mumbai)**

🚆 Available on:
• Western Line  
• Central Line  

💺 Fully air-conditioned coaches  
🎟️ Higher fare than First Class  
⏱️ Lower frequency than regular locals  

📍 Platforms may differ — check display boards  

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

def find_interchange(src_line, dst_line):
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

    # ---------- INFORMATION INTENTS FIRST ----------
    if "senior" in q:
        return SENIOR_CITIZEN

    if "student" in q:
        return STUDENT_CONCESSION

    if "monthly" in q or "quarterly" in q or "season" in q or "pass" in q:
        return MONTHLY_PASS

    if "luggage" in q:
        return LUGGAGE_RULES

    if "ac train" in q or "ac local" in q:
        return AC_TRAINS

    # ---------- ROUTE LOGIC ----------
    stations = extract_stations(query)

    if len(stations) < 2:
        return (
            "❌ I couldn’t identify both source and destination.\n\n"
            "Try:\n"
            "• Dadar to Churchgate\n"
            "• Sion to Grant Road\n"
            "• Senior citizen concession\n"
            "• Monthly pass fees\n"
            "• Luggage rules"
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

🚉 **Change at:** {interchange}

Steps:
1. Take a **{src_line}** local from **{src} → {interchange}**
2. Change to **{dst_line}**
3. Continue from **{interchange} → {dst}**

⚠️ Platform numbers may vary. Check station display boards.
"""

    return f"""
🚆 **Route Information**

From: **{src}**  
To: **{dst}**

Line: **{src_line}**

• Direct local trains available  
• Frequency depends on time of day  

⚠️ Check station display boards for platform numbers.
"""
