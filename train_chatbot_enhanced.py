# ==================================================
# Mumbai Local Train Assistant – Core Logic (FINAL)
# ==================================================

from difflib import get_close_matches
import pandas as pd
from datetime import datetime
import os
import re

# Import first/last mile bus connections
try:
    from bus_connections import check_needs_bus_connection, format_bus_response, get_combined_route, FIRST_LAST_MILE
    BUS_CONNECTIONS_AVAILABLE = True
except ImportError:
    BUS_CONNECTIONS_AVAILABLE = False

# Import fare calculator
try:
    from fare_calculator import calculate_fare, format_fare_response
    FARE_CALCULATOR_AVAILABLE = True
except ImportError:
    FARE_CALCULATOR_AVAILABLE = False

# Import station info (platforms, peak hours, metro)
try:
    from station_info import (
        format_platform_response, get_peak_hour_info, get_metro_info,
        get_platform_info, CROWDED_STATIONS
    )
    STATION_INFO_AVAILABLE = True
except ImportError:
    STATION_INFO_AVAILABLE = False

# Import language support
try:
    from language_support import detect_language, normalize_query
    LANGUAGE_SUPPORT_AVAILABLE = True
except ImportError:
    LANGUAGE_SUPPORT_AVAILABLE = False

# ---------------- TRAIN DATA FILES ----------------

BASE_DIR = os.path.dirname(__file__)
AC_TRAIN_FILE = os.path.join(BASE_DIR, "mumbai_ac_trains.csv")
LOCAL_TRAIN_FILE = os.path.join(BASE_DIR, "mumbai_local_trains.csv")


def load_trains(ac_only=False):
    """Load train schedule from CSV files."""
    try:
        if ac_only:
            return pd.read_csv(AC_TRAIN_FILE)
        else:
            # Try to load non-AC trains, fall back to AC if not available
            try:
                return pd.read_csv(LOCAL_TRAIN_FILE)
            except FileNotFoundError:
                return pd.read_csv(AC_TRAIN_FILE)
    except FileNotFoundError:
        return None


def parse_time(t):
    """Parse time string to time object."""
    try:
        # Handle different time formats
        t = t.strip().lower()
        for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
            try:
                return datetime.strptime(t, fmt).time()
            except:
                continue
        return None
    except:
        return None


def extract_time_from_query(query):
    """Extract time from user query like 'at 1 pm', 'around 3:30', 'after 5pm'."""
    q = query.lower()

    # Patterns to match time in query
    patterns = [
        # "at 1 pm", "at 1:30 pm", "at 1pm", "at 5 p"
        r'(?:at|around|after|by)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm|a|p)\b',
        # "1 pm", "1:30 pm", "5p", "5 p" (standalone)
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a|p)\b',
        # "13:00", "14:30" (24-hour format)
        r'(\d{1,2}):(\d{2})(?!\s*(?:am|pm))',
    ]

    for pattern in patterns:
        match = re.search(pattern, q)
        if match:
            groups = match.groups()

            if len(groups) == 3:  # 12-hour format with am/pm
                hour = int(groups[0])
                minute = int(groups[1]) if groups[1] else 0
                period = groups[2]

                # Handle shorthand "a" for "am" and "p" for "pm"
                if period in ['p', 'pm']:
                    if hour != 12:
                        hour += 12
                elif period in ['a', 'am']:
                    if hour == 12:
                        hour = 0

                try:
                    return datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                except:
                    pass

            elif len(groups) == 2:  # 24-hour format
                hour = int(groups[0])
                minute = int(groups[1])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    try:
                        return datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                    except:
                        pass

    return None


def get_trains(source=None, dest=None, line=None, ac_only=False, limit=8, after_time=None, show_all=False):
    """Get trains based on filters.

    Args:
        after_time: Show trains after this specific time (datetime.time object)
        show_all: If True, show all trains regardless of time
    """
    df = load_trains(ac_only=ac_only)
    if df is None or len(df) == 0:
        return None, False

    # Filter by criteria
    if line:
        df = df[df['line'] == line]
    if source:
        # Flexible matching for source - handle variations like "CSMT", "Mumbai CSMT", "Cst"
        src_lower = source.lower().replace('csmt', '').replace('cst', '').strip()
        if src_lower:
            df = df[df['source'].str.lower().str.contains(src_lower, na=False)]
        else:
            # Searching for CSMT/CST specifically
            df = df[df['source'].str.lower().str.contains('csmt|cst|mumbai c', regex=True, na=False)]
    if dest:
        # Flexible matching for destination
        dst_lower = dest.lower().replace('csmt', '').replace('cst', '').strip()
        if dst_lower:
            df = df[df['dest'].str.lower().str.contains(dst_lower, na=False)]
        else:
            df = df[df['dest'].str.lower().str.contains('csmt|cst|mumbai c', regex=True, na=False)]

    if len(df) == 0:
        return None, False

    # Sort by time
    df = df.copy()
    df['parsed_time'] = df['time'].apply(parse_time)

    total_trains = len(df)
    has_more = False

    if show_all:
        # Show all trains sorted by time
        upcoming = df.sort_values('parsed_time')
    else:
        # Filter by time
        filter_time = after_time if after_time else datetime.now().time()
        upcoming = df[df['parsed_time'] >= filter_time]

        if len(upcoming) == 0:
            # If no trains left, show first trains of the day
            upcoming = df.sort_values('parsed_time')
        else:
            upcoming = upcoming.sort_values('parsed_time')
            has_more = total_trains > len(upcoming)

    result = upcoming.drop(columns=['parsed_time'], errors='ignore').head(limit)
    return result, has_more, total_trains


# ---------------- STATION DATA ----------------

CENTRAL_STATIONS = [
    "CSMT", "Masjid", "Byculla", "Chinchpokli", "Currey Road",
    "Parel", "Dadar", "Matunga", "Sion", "Kurla",
    "Vidyavihar", "Ghatkopar", "Vikhroli", "Kanjurmarg",
    "Bhandup", "Nahur", "Mulund", "Thane", "Kalyan",
    "Dombivli", "Ambernath", "Badlapur", "Titwala", "Kasara", "Karjat"
]

WESTERN_STATIONS = [
    "Churchgate", "Marine Lines", "Charni Road", "Grant Road",
    "Mumbai Central", "Mahalakshmi", "Lower Parel", "Prabhadevi",
    "Dadar", "Mahim Junction", "Bandra", "Khar Road",
    "Santacruz", "Vile Parle", "Andheri", "Jogeshwari",
    "Goregaon", "Malad", "Kandivali", "Borivali",
    "Dahisar", "Mira Road", "Bhayandar",
    "Vasai Road", "Nalla Sopara", "NallaSopara", "Virar"
]

HARBOUR_STATIONS = [
    "CSMT", "Masjid", "Sandhurst Road", "Dockyard Road",
    "Sewri", "Vadala Road", "Kurla", "Chembur",
    "Govandi", "Mankhurd", "Vashi", "Sanpada",
    "Belapur CBD", "Belapur", "Nerul", "Panvel"
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
    # Try exact match first (case-insensitive)
    word_lower = word.lower()
    for station in ALL_STATIONS:
        if station.lower() == word_lower:
            return station

    # Try fuzzy match
    match = get_close_matches(word, ALL_STATIONS, n=1, cutoff=0.6)
    if match:
        return match[0]

    # Try with title case
    match = get_close_matches(word.title(), ALL_STATIONS, n=1, cutoff=0.6)
    return match[0] if match else None


def extract_stations(query):
    # Words to ignore (not station names)
    ignore_words = {'train', 'trains', 'from', 'to', 'the', 'a', 'an', 'on', 'at',
                    'line', 'local', 'fast', 'slow', 'ac', 'next', 'show', 'get',
                    'western', 'central', 'harbour', 'harbor', 'railway',
                    'fare', 'price', 'cost', 'ticket', 'kitna', 'rate', 'charge',
                    'how', 'much', 'what', 'is', 'for', 'between'}

    found = []
    words = query.replace(',', ' ').replace(' to ', ' ').split()
    for w in words:
        if w.lower() in ignore_words:
            continue
        s = fuzzy_station(w)
        if s and s not in found:
            found.append(s)
    return found


def determine_line(station):
    station_lower = station.lower()
    for s in CENTRAL_STATIONS:
        if s.lower() == station_lower:
            return ("Central Line", "CR")
    for s in HARBOUR_STATIONS:
        if s.lower() == station_lower:
            return ("Harbour Line", "HR")
    return ("Western Line", "WR")


def find_interchange(src_line, dst_line):
    if src_line == dst_line:
        return None
    if {"Central Line", "Western Line"} == {src_line, dst_line}:
        return "Dadar"
    if {"Central Line", "Harbour Line"} == {src_line, dst_line}:
        return "Kurla"
    if {"Western Line", "Harbour Line"} == {src_line, dst_line}:
        return "Dadar → Kurla"
    return None


# ---------------- AC TRAIN HANDLER ----------------

def handle_ac_query(q, original_query):
    """Handle AC train related queries."""

    # Detect line from query
    line = None
    line_name = None
    if "western" in q or " wr " in f" {q} ":
        line = "WR"
        line_name = "Western Line"
    elif "central" in q or " cr " in f" {q} ":
        line = "CR"
        line_name = "Central Line"
    elif "harbour" in q or "harbor" in q or " hr " in f" {q} ":
        line = "HR"
        line_name = "Harbour Line"

    # Extract stations from query
    stations = extract_stations(original_query)
    source = stations[0] if len(stations) >= 1 else None
    dest = stations[1] if len(stations) >= 2 else None

    # Get AC trains based on filters
    if line and not source:
        trains, has_more, total = get_trains(line=line, ac_only=True, limit=8)
        if trains is None or len(trains) == 0:
            return f"No AC train data available for {line_name}."

        result = f"**AC Trains on {line_name}**\n\n"
        result += "| Time | From | To | Type |\n|------|------|-----|------|\n"
        for _, row in trains.iterrows():
            result += f"| {row['time']} | {row['source']} | {row['dest']} | {row['type']} |\n"
        result += f"\n_Showing {len(trains)} upcoming AC trains_"
        return result

    elif source:
        trains, has_more, total = get_trains(source=source, dest=dest, ac_only=True, limit=8)

        if trains is None or len(trains) == 0:
            return f"No AC trains found from **{source}**" + (f" to **{dest}**" if dest else "") + ".\n\nAC trains run on limited routes. Try: Churchgate, Virar, Borivali, Bhayandar"

        dest_text = f" to **{dest}**" if dest else ""
        result = f"**AC Trains from {source}**{dest_text}\n\n"
        result += "| Time | To | Type |\n|------|-----|------|\n"
        for _, row in trains.iterrows():
            result += f"| {row['time']} | {row['dest']} | {row['type']} |\n"
        result += f"\n_Showing {len(trains)} upcoming AC trains_"
        return result

    else:
        # General AC train info
        df = load_trains(ac_only=True)
        if df is None:
            return "❌ AC train schedule not available."

        wr_count = len(df[df['line'] == 'WR']) if 'line' in df.columns else 0
        cr_count = len(df[df['line'] == 'CR']) if 'line' in df.columns else 0
        hr_count = len(df[df['line'] == 'HR']) if 'line' in df.columns else 0

        return f"""
🚆 **AC Local Trains – Mumbai Suburban**

AC locals run on Western Line (most frequent):

| Line | Trains/Day |
|------|------------|
| Western (WR) | {wr_count} |
| Central (CR) | {cr_count} |
| Harbour (HR) | {hr_count} |

💡 **Tips:**
• AC trains have higher frequency during peak hours
• First class AC fare is approximately ₹60-105
• AC coaches are marked with blue stripe

Try asking:
• "AC trains on Western line"
• "AC train from Churchgate"
• "AC train from Virar to Borivali"
"""


# ---------------- TRAIN TIMETABLE HANDLER ----------------

def handle_train_query(src, dst, line_code, after_time=None, show_all=False):
    """Handle train timetable queries."""

    # Try to find trains
    trains, has_more, total = get_trains(source=src, dest=dst, limit=10, after_time=after_time, show_all=show_all)

    if trains is None or len(trains) == 0:
        # Try reverse direction or broader search
        trains, has_more, total = get_trains(source=src, limit=10, after_time=after_time, show_all=show_all)

    if trains is not None and len(trains) > 0:
        time_note = ""
        if after_time:
            time_note = f" (after {after_time.strftime('%I:%M %p')})"
        result = f"**Trains from {src} to {dst}**{time_note}\n\n"
        result += "| Time | Destination | Type |\n|------|-------------|------|\n"
        for _, row in trains.iterrows():
            result += f"| {row['time']} | {row['dest']} | {row['type']} |\n"
        result += f"\n_Showing {len(trains)} of {total} trains_"
        if has_more:
            result += f"\n_Say \"all trains {src} to {dst}\" for full schedule_"
        return result

    return None


# ---------------- BUS + TRAIN COMBINED ROUTE ----------------

def handle_bus_train_route(query, from_area, to_area):
    """Handle queries that need bus + train combinations."""
    q_lower = query.lower()

    response = ""
    start_station = None
    end_station = None
    step_num = 1

    # Extract regular stations from query
    stations = extract_stations(query)

    # First mile (from area to train station)
    if from_area:
        conn = from_area["nearest_stations"][0]
        start_station = conn["station"]
        response += f"**Step {step_num}: Bus from {from_area['area_name']}**\n"
        response += f"Take Bus **{' or '.join(conn['buses'])}** to **{conn['station']}** Station\n"
        response += f"Time: {conn['travel_time']}\n"
        if conn.get("notes"):
            response += f"_{conn['notes']}_\n"
        response += "\n"
        step_num += 1
    elif stations:
        # Source is a regular station
        start_station = stations[0]

    # Determine end station
    if to_area:
        conn = to_area["nearest_stations"][0]
        end_station = conn["station"]
    elif len(stations) >= 2:
        end_station = stations[1]
    elif len(stations) == 1 and from_area:
        end_station = stations[0]

    # Get train route
    if start_station and end_station and start_station != end_station:
        src_line, _ = determine_line(start_station)
        dst_line, _ = determine_line(end_station)
        interchange = find_interchange(src_line, dst_line)

        response += f"**Step {step_num}: Train**\n"
        if interchange and interchange != end_station and interchange != start_station:
            response += f"**{start_station}** -> **{interchange}** (change) -> **{end_station}**\n"
        else:
            response += f"**{start_station}** -> **{end_station}** ({src_line})\n"
        response += "\n"
        step_num += 1

    # Last mile (from train station to destination area)
    if to_area:
        conn = to_area["nearest_stations"][0]
        response += f"**Step {step_num}: Bus to {to_area['area_name']}**\n"
        response += f"From **{conn['station']}** take Bus **{' or '.join(conn['buses'])}**\n"
        response += f"Time: {conn['travel_time']}\n"
        if conn.get("notes"):
            response += f"_{conn['notes']}_\n"

    return response


# ---------------- CHATBOT RESPONSE ----------------

def chatbot_response(query: str):

    # Normalize Hindi/Marathi queries to English
    if LANGUAGE_SUPPORT_AVAILABLE:
        lang = detect_language(query)
        if lang in ["hindi", "marathi"]:
            query = normalize_query(query)

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

    # ---- PLATFORM INFO ----
    if STATION_INFO_AVAILABLE and ("platform" in q or "which platform" in q):
        stations = extract_stations(query)
        if stations:
            platform_info = format_platform_response(stations[0])
            if platform_info:
                return platform_info
        return "Which station? Try: *Platform info Dadar*"

    # ---- PEAK HOURS ----
    if STATION_INFO_AVAILABLE and ("peak" in q or "rush" in q or "crowd" in q or "busy" in q):
        return get_peak_hour_info()

    # ---- METRO INFO ----
    if STATION_INFO_AVAILABLE and ("metro" in q or "line 1" in q or "versova" in q and "ghatkopar" in q):
        return get_metro_info()

    # ---- FARE CALCULATOR ----
    fare_keywords = ["fare", "price", "cost", "ticket", "kitna", "rate", "charge"]
    if FARE_CALCULATOR_AVAILABLE and any(kw in q for kw in fare_keywords):
        stations = extract_stations(query)
        if len(stations) >= 2:
            fare_data = calculate_fare(stations[0], stations[1])
            if fare_data:
                return format_fare_response(fare_data)

    # ---- BUS + TRAIN COMBINED ROUTE ----
    if BUS_CONNECTIONS_AVAILABLE:
        # Split query by "to" to identify source and destination
        from_area = None
        to_area = None

        if " to " in q:
            parts = q.split(" to ", 1)
            from_part = parts[0].strip()
            to_part = parts[1].strip()

            _, _, from_area = check_needs_bus_connection(from_part)
            _, _, to_area = check_needs_bus_connection(to_part)
        else:
            # Check entire query
            _, _, from_area = check_needs_bus_connection(q)

        if from_area or to_area:
            result = "**Combined Bus + Train Route**\n\n"
            result += handle_bus_train_route(query, from_area, to_area)
            return result

    # ---- AC TRAIN LOGIC ----
    if "ac" in q or "air condition" in q:
        return handle_ac_query(q, query)

    # ---- ROUTE / TRAIN LOGIC ----
    stations = extract_stations(query)

    # Extract time from query if specified
    query_time = extract_time_from_query(query)
    show_all = "all train" in q or "full schedule" in q or "all schedule" in q

    if len(stations) < 2:
        # Check if asking about trains from a single station
        if len(stations) == 1:
            trains, has_more, total = get_trains(source=stations[0], limit=8, after_time=query_time, show_all=show_all)
            if trains is not None and len(trains) > 0:
                time_note = ""
                if query_time:
                    time_note = f" (after {query_time.strftime('%I:%M %p')})"
                result = f"**Trains from {stations[0]}**{time_note}\n\n"
                result += "| Time | Destination | Type |\n|------|-------------|------|\n"
                for _, row in trains.iterrows():
                    result += f"| {row['time']} | {row['dest']} | {row['type']} |\n"
                result += f"\n_Showing {len(trains)} of {total} trains_"
                if has_more and not show_all:
                    result += f"\n_Say \"all trains from {stations[0]}\" for full schedule_"
                return result

        return (
            "I couldn't identify the stations.\n\n"
            "Try:\n- Dadar to Churchgate\n- Trains from CSMT\n- AC trains on Western line\n- Student concession"
        )

    src, dst = stations[0], stations[1]

    if src == dst:
        return "⚠️ Source and destination cannot be the same."

    src_line, src_code = determine_line(src)
    dst_line, dst_code = determine_line(dst)

    # Try to get actual train timings
    train_result = handle_train_query(src, dst, src_code, after_time=query_time, show_all=show_all)

    if train_result:
        return train_result

    # Fall back to route information
    interchange = find_interchange(src_line, dst_line)

    if interchange:
        return f"""
🔁 **Route Information**

From: **{src}** ({src_line})
To: **{dst}** ({dst_line})

🚉 Change at **{interchange}**

1. {src} → {interchange.split('→')[0].strip()} ({src_line})
2. Switch to {dst_line}
3. Continue to {dst}

_Tip: Ask "trains from {src}" for live timings_
"""

    return f"""
🚆 **Route Information**

From: **{src}**
To: **{dst}**

Line: **{src_line}**

• Direct locals available
• Platform depends on direction

_Tip: Ask "trains from {src}" for live timings_
"""
