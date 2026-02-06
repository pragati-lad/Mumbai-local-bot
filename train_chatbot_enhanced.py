# ==================================================
# Mumbai Local Train Assistant – Core Logic (FINAL)
# ==================================================

from difflib import get_close_matches
import pandas as pd
from datetime import datetime
import os

# ---------------- AC TRAIN DATA ----------------

AC_TRAIN_FILE = os.path.join(os.path.dirname(__file__), "mumbai_ac_trains.csv")

def load_ac_trains():
    """Load AC train schedule from CSV."""
    try:
        return pd.read_csv(AC_TRAIN_FILE)
    except FileNotFoundError:
        return None

def get_ac_trains_by_line(line_code):
    """Get AC trains for a specific line (WR, CR, HR)."""
    df = load_ac_trains()
    if df is None:
        return None
    return df[df['line'] == line_code]

def get_next_ac_trains(source=None, dest=None, line=None, limit=5):
    """Get upcoming AC trains based on filters."""
    df = load_ac_trains()
    if df is None:
        return None

    # Get current time
    now = datetime.now()
    current_time_str = now.strftime("%I:%M %p")

    # Filter by criteria
    if line:
        df = df[df['line'] == line]
    if source:
        df = df[df['source'].str.lower() == source.lower()]
    if dest:
        df = df[df['dest'].str.lower() == dest.lower()]

    # Try to filter trains after current time
    def parse_time(t):
        try:
            return datetime.strptime(t, "%I:%M %p").time()
        except:
            return None

    df = df.copy()
    df['parsed_time'] = df['time'].apply(parse_time)
    current_time = now.time()

    # Get trains after current time
    upcoming = df[df['parsed_time'] >= current_time].head(limit)

    if len(upcoming) == 0:
        # If no trains left today, show first trains
        upcoming = df.head(limit)

    return upcoming.drop(columns=['parsed_time'], errors='ignore')

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
🎟️ **Monthly / Quarterly Pass – Mumbai Local Trains**

📌 Prices depend on **distance & class** (approximate ranges):

**Second Class**
• Monthly: ₹100 – ₹300  
• Quarterly: ₹300 – ₹900  

**First Class**
• Monthly: ₹400 – ₹1200  
• Quarterly: ₹1200 – ₹3600  

🎓 Student & 👴 Senior citizen concessions applicable  
📍 Issued at suburban ticket counters  

_Source: Indian Railways_
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

# ---------------- AC TRAIN HANDLER ----------------

def handle_ac_query(q, original_query):
    """Handle AC train related queries."""

    # Detect line from query
    line = None
    if "western" in q or "wr" in q:
        line = "WR"
        line_name = "Western Line"
    elif "central" in q or "cr" in q:
        line = "CR"
        line_name = "Central Line"
    elif "harbour" in q or "harbor" in q or "hr" in q:
        line = "HR"
        line_name = "Harbour Line"

    # Extract stations from query
    stations = extract_stations(original_query)
    source = stations[0] if len(stations) >= 1 else None
    dest = stations[1] if len(stations) >= 2 else None

    # Get AC trains based on filters
    if line and not source:
        # Query for specific line
        trains = get_next_ac_trains(line=line, limit=6)
        if trains is None or len(trains) == 0:
            return f"❌ No AC train data available for {line_name}."

        result = f"🚆 **AC Trains on {line_name}**\n\n"
        result += "| Time | From | To | Type |\n|------|------|-----|------|\n"
        for _, row in trains.iterrows():
            result += f"| {row['time']} | {row['source']} | {row['dest']} | {row['type']} |\n"
        result += f"\n_Showing next {len(trains)} AC trains_"
        return result

    elif source:
        # Query for specific source/destination
        trains = get_next_ac_trains(source=source, dest=dest, limit=6)
        if trains is None or len(trains) == 0:
            # Try with fuzzy matching
            fuzzy_src = fuzzy_station(source) if source else None
            if fuzzy_src:
                trains = get_next_ac_trains(source=fuzzy_src, dest=dest, limit=6)

        if trains is None or len(trains) == 0:
            return f"❌ No AC trains found from **{source}**" + (f" to **{dest}**" if dest else "") + ".\n\nAC trains run on limited routes. Try: Churchgate, CSMT, Thane, Borivali, Panvel"

        dest_text = f" to **{dest}**" if dest else ""
        result = f"🚆 **AC Trains from {source}**{dest_text}\n\n"
        result += "| Time | To | Line | Type |\n|------|-----|------|------|\n"
        for _, row in trains.iterrows():
            result += f"| {row['time']} | {row['dest']} | {row['line']} | {row['type']} |\n"
        result += f"\n_Showing next {len(trains)} AC trains_"
        return result

    else:
        # General AC train info
        df = load_ac_trains()
        if df is None:
            return "❌ AC train schedule not available."

        wr_count = len(df[df['line'] == 'WR'])
        cr_count = len(df[df['line'] == 'CR'])
        hr_count = len(df[df['line'] == 'HR'])

        return f"""
🚆 **AC Local Trains – Mumbai Suburban**

AC locals run on all three lines:

| Line | Trains/Day | Frequency |
|------|------------|-----------|
| Western (WR) | {wr_count} | Every 35-60 mins |
| Central (CR) | {cr_count} | Every 50-90 mins |
| Harbour (HR) | {hr_count} | Every 90-180 mins |

💡 **Tips:**
• AC trains have higher frequency during peak hours
• First class AC fare is approximately ₹60-105
• AC coaches are marked with blue stripe

Try asking:
• "AC trains on Western line"
• "AC train from Churchgate"
• "Next AC train from CSMT to Thane"
"""


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

    # ---- AC TRAIN LOGIC ----
    if "ac" in q or "air" in q or "conditioned" in q:
        return handle_ac_query(q, query)

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
