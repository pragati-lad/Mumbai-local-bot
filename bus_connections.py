# ==================================================
# Mumbai Local Train - First/Last Mile Bus Connections
# ==================================================
# Real BEST bus routes connecting areas without train
# stations to the nearest railway stations
# ==================================================

# Areas mapped to nearest stations with real bus routes
FIRST_LAST_MILE = {
    # ==================== POWAI / HIRANANDANI ====================
    "powai": {
        "area_name": "Powai / Hiranandani",
        "nearest_stations": [
            {
                "station": "Kanjurmarg",
                "line": "Central",
                "buses": ["602", "496"],
                "travel_time": "15-20 min",
                "notes": "602 is the most frequent - runs every 10-15 min"
            },
            {
                "station": "Vikhroli",
                "line": "Central",
                "buses": ["418", "185"],
                "travel_time": "15-20 min",
                "notes": "185 goes to Powai Vihar/Lake Homes side"
            }
        ],
        "keywords": ["powai", "hiranandani", "iit bombay", "iit", "chandivali", "powai lake"]
    },

    # ==================== JUHU ====================
    "juhu": {
        "area_name": "Juhu",
        "nearest_stations": [
            {
                "station": "Vile Parle",
                "line": "Western",
                "buses": ["203", "231", "224"],
                "travel_time": "15-20 min",
                "notes": "203 is most frequent - every 20 min"
            },
            {
                "station": "Andheri",
                "line": "Western",
                "buses": ["203", "A-203", "231"],
                "travel_time": "20-25 min",
                "notes": "A-203 is AC bus"
            },
            {
                "station": "Santacruz",
                "line": "Western",
                "buses": ["28", "56", "A-56"],
                "travel_time": "15-20 min",
                "notes": "A-56 is AC bus"
            }
        ],
        "keywords": ["juhu", "juhu beach", "juhu tara", "irla"]
    },

    # ==================== BKC (BANDRA KURLA COMPLEX) ====================
    "bkc": {
        "area_name": "Bandra Kurla Complex (BKC)",
        "nearest_stations": [
            {
                "station": "Bandra",
                "line": "Western/Harbour",
                "buses": ["316", "317", "182", "183", "BKC-1", "BKC-2"],
                "travel_time": "10-15 min",
                "notes": "BKC-1 and BKC-2 are AC buses. 183 is women special"
            },
            {
                "station": "Kurla",
                "line": "Central/Harbour",
                "buses": ["303", "310", "BKC-22"],
                "travel_time": "10-15 min",
                "notes": "303 runs every 20 min"
            }
        ],
        "keywords": ["bkc", "bandra kurla", "diamond market", "mmrda", "platina"]
    },

    # ==================== NARIMAN POINT / CUFFE PARADE ====================
    "nariman_point": {
        "area_name": "Nariman Point / Cuffe Parade",
        "nearest_stations": [
            {
                "station": "Churchgate",
                "line": "Western",
                "buses": ["121", "137", "138", "106"],
                "travel_time": "5-10 min",
                "notes": "121 runs every 15 min"
            },
            {
                "station": "Marine Lines",
                "line": "Western",
                "buses": ["121", "100", "A-108"],
                "travel_time": "5-8 min",
                "notes": "A-108 is AC bus"
            }
        ],
        "keywords": ["nariman point", "cuffe parade", "mantralaya", "ncpa", "world trade center", "wtc"]
    },

    # ==================== WORLI ====================
    "worli": {
        "area_name": "Worli",
        "nearest_stations": [
            {
                "station": "Lower Parel",
                "line": "Western",
                "buses": ["110", "28", "83", "A-125", "168"],
                "travel_time": "10-15 min",
                "notes": "110 and 28 are most frequent"
            },
            {
                "station": "Dadar",
                "line": "Western/Central",
                "buses": ["385", "A-118", "A-167"],
                "travel_time": "15-20 min",
                "notes": "A-118 and A-167 are AC buses"
            }
        ],
        "keywords": ["worli", "worli sea face", "worli naka", "worli village", "haji ali"]
    },

    # ==================== LOKHANDWALA / OSHIWARA ====================
    "lokhandwala": {
        "area_name": "Lokhandwala / Oshiwara",
        "nearest_stations": [
            {
                "station": "Andheri",
                "line": "Western",
                "buses": ["A-180", "251", "266"],
                "travel_time": "10-15 min",
                "notes": "A-180 runs every 10-15 min"
            },
            {
                "station": "Goregaon",
                "line": "Western",
                "buses": ["261", "251"],
                "travel_time": "10-12 min",
                "notes": "From Oshiwara Depot"
            }
        ],
        "keywords": ["lokhandwala", "oshiwara", "andheri lokhandwala", "lokhandwala market", "four bungalows"]
    },

    # ==================== COLABA ====================
    "colaba": {
        "area_name": "Colaba",
        "nearest_stations": [
            {
                "station": "Churchgate",
                "line": "Western",
                "buses": ["3", "11", "103", "132"],
                "travel_time": "15-20 min",
                "notes": "3 and 11 are frequent routes"
            },
            {
                "station": "CST",
                "line": "Central/Harbour",
                "buses": ["1", "3", "21", "125"],
                "travel_time": "15-20 min",
                "notes": "Multiple stops along Colaba Causeway"
            }
        ],
        "keywords": ["colaba", "colaba causeway", "gateway of india", "taj hotel", "regal"]
    },

    # ==================== GOREGAON EAST (NESCO/OBEROI) ====================
    "goregaon_east": {
        "area_name": "Goregaon East (NESCO/Oberoi)",
        "nearest_stations": [
            {
                "station": "Goregaon",
                "line": "Western",
                "buses": ["460", "462", "467"],
                "travel_time": "10-15 min",
                "notes": "Cross over via FOB from Western to East"
            },
            {
                "station": "Ram Mandir (Metro)",
                "line": "Metro Line 1",
                "buses": ["460"],
                "travel_time": "5-10 min",
                "notes": "Metro connects to Ghatkopar on Central"
            }
        ],
        "keywords": ["nesco", "goregaon east", "oberoi", "oberoi mall", "hub mall", "westin"]
    },

    # ==================== MALAD WEST (INORBIT/MINDSPACE) ====================
    "malad_west": {
        "area_name": "Malad West (Inorbit/Mindspace)",
        "nearest_stations": [
            {
                "station": "Malad",
                "line": "Western",
                "buses": ["268", "269", "271"],
                "travel_time": "10-15 min",
                "notes": "From station west side to Inorbit"
            }
        ],
        "keywords": ["inorbit", "mindspace malad", "malad west", "infinity mall", "evershine"]
    },

    # ==================== ANDHERI EAST (SEEPZ/MIDC) ====================
    "andheri_east": {
        "area_name": "Andheri East (SEEPZ/MIDC)",
        "nearest_stations": [
            {
                "station": "Andheri",
                "line": "Western/Metro",
                "buses": ["309", "332", "335", "350"],
                "travel_time": "15-20 min",
                "notes": "Take Metro Line 1 for faster travel to SEEPZ"
            },
            {
                "station": "Marol Naka (Metro)",
                "line": "Metro Line 1",
                "buses": ["350", "332"],
                "travel_time": "5-10 min",
                "notes": "Closest for MIDC area"
            }
        ],
        "keywords": ["seepz", "midc andheri", "marol", "saki naka", "chakala"]
    },

    # ==================== THANE WEST (VIVIANA/LAKE CITY) ====================
    "thane_west": {
        "area_name": "Thane West (Viviana/Lake City Mall)",
        "nearest_stations": [
            {
                "station": "Thane",
                "line": "Central",
                "buses": ["TMT-1", "TMT-3", "TMT-88"],
                "travel_time": "10-15 min",
                "notes": "TMT buses operate in Thane. Viviana is 3km from station"
            }
        ],
        "keywords": ["viviana", "thane west", "lake city", "hiranandani thane", "ghodbunder"]
    },

    # ==================== AIROLI / GHANSOLI ====================
    "airoli": {
        "area_name": "Airoli / Ghansoli",
        "nearest_stations": [
            {
                "station": "Airoli",
                "line": "Harbour (Trans-Harbour)",
                "buses": ["NMMT-11", "NMMT-21"],
                "travel_time": "5-10 min",
                "notes": "NMMT buses. Airoli station connects to Thane/CST"
            }
        ],
        "keywords": ["airoli", "ghansoli", "mindspace airoli", "l&t"]
    },

    # ==================== VASHI / BELAPUR CBD ====================
    "vashi_cbd": {
        "area_name": "Vashi / CBD Belapur",
        "nearest_stations": [
            {
                "station": "Vashi",
                "line": "Harbour",
                "buses": ["NMMT-51", "NMMT-52"],
                "travel_time": "10-15 min",
                "notes": "NMMT buses in Navi Mumbai"
            },
            {
                "station": "CBD Belapur",
                "line": "Harbour",
                "buses": ["NMMT-55"],
                "travel_time": "5-10 min",
                "notes": "For Belapur station area"
            }
        ],
        "keywords": ["vashi", "belapur", "cbd belapur", "inorbit vashi", "raghuleela"]
    },

    # ==================== BANDRA WEST ====================
    "bandra_west": {
        "area_name": "Bandra West (Linking Road/Hill Road)",
        "nearest_stations": [
            {
                "station": "Bandra",
                "line": "Western/Harbour",
                "buses": ["210", "211", "215"],
                "travel_time": "10-15 min",
                "notes": "Walk to Linking Road from station west"
            }
        ],
        "keywords": ["linking road", "hill road", "bandra west", "pali hill", "bandstand", "carter road"]
    },

    # ==================== CHEMBUR ====================
    "chembur": {
        "area_name": "Chembur",
        "nearest_stations": [
            {
                "station": "Chembur",
                "line": "Harbour",
                "buses": ["354", "356", "371"],
                "travel_time": "5-10 min",
                "notes": "Chembur station on Harbour line"
            },
            {
                "station": "Kurla",
                "line": "Central/Harbour",
                "buses": ["362", "364"],
                "travel_time": "15-20 min",
                "notes": "For Central line connections"
            }
        ],
        "keywords": ["chembur", "rcd", "diamond garden", "chembur east"]
    },

    # ==================== VERSOVA ====================
    "versova": {
        "area_name": "Versova",
        "nearest_stations": [
            {
                "station": "Andheri",
                "line": "Western",
                "buses": ["203", "231", "234"],
                "travel_time": "20-25 min",
                "notes": "Or take Metro from Versova to Andheri"
            },
            {
                "station": "Versova (Metro)",
                "line": "Metro Line 1",
                "buses": [],
                "travel_time": "Direct Metro",
                "notes": "Metro to Andheri (Western) or Ghatkopar (Central)"
            }
        ],
        "keywords": ["versova", "versova beach", "yari road", "seven bungalows", "4 bungalows"]
    },

    # ==================== MULUND WEST ====================
    "mulund_west": {
        "area_name": "Mulund West",
        "nearest_stations": [
            {
                "station": "Mulund",
                "line": "Central",
                "buses": ["460", "466"],
                "travel_time": "10-15 min",
                "notes": "Cross FOB to West side"
            }
        ],
        "keywords": ["mulund west", "johnson", "r city mall", "nirmal lifestyle"]
    },

    # ==================== SANTACRUZ EAST ====================
    "santacruz_east": {
        "area_name": "Santacruz East (Kalina)",
        "nearest_stations": [
            {
                "station": "Santacruz",
                "line": "Western",
                "buses": ["318", "321", "324"],
                "travel_time": "10-15 min",
                "notes": "Kalina is east of Santacruz station"
            }
        ],
        "keywords": ["kalina", "santacruz east", "cst road", "vidyanagari", "mumbai university"]
    },

    # ==================== LOWER PAREL / WORLI ====================
    "lower_parel": {
        "area_name": "Lower Parel (Phoenix/High Street)",
        "nearest_stations": [
            {
                "station": "Lower Parel",
                "line": "Western",
                "buses": ["83", "84", "85"],
                "travel_time": "5-10 min",
                "notes": "Phoenix Mall is 5 min walk from station"
            }
        ],
        "keywords": ["phoenix", "high street", "kamala mills", "palladium", "one indiabulls"]
    }
}


def find_area(query):
    """Find matching area from query."""
    query_lower = query.lower()

    for area_key, area_data in FIRST_LAST_MILE.items():
        for keyword in area_data["keywords"]:
            if keyword in query_lower:
                return area_key, area_data

    return None, None


def get_bus_connection(from_area, to_station=None):
    """Get bus connection details for an area."""
    area_key, area_data = find_area(from_area)

    if not area_data:
        return None

    return area_data


def format_bus_response(area_data, destination=None):
    """Format bus connection info for chatbot response."""
    response = f"\n\n**Getting to/from {area_data['area_name']}**\n\n"

    for conn in area_data["nearest_stations"]:
        station = conn["station"]
        line = conn["line"]
        buses = ", ".join(conn["buses"])
        time = conn["travel_time"]
        notes = conn.get("notes", "")

        response += f"**{station}** ({line} Line)\n"
        response += f"- Buses: {buses}\n"
        response += f"- Time: {time}\n"
        if notes:
            response += f"- {notes}\n"
        response += "\n"

    return response


def get_combined_route(from_place, to_place, train_route_func):
    """
    Get combined bus + train route.

    Args:
        from_place: Starting location (could be area or station)
        to_place: Destination (could be area or station)
        train_route_func: Function to get train route between stations

    Returns:
        Combined route info with first/last mile buses
    """
    from_area_key, from_area = find_area(from_place)
    to_area_key, to_area = find_area(to_place)

    result = {
        "from": from_place,
        "to": to_place,
        "first_mile": None,
        "train_route": None,
        "last_mile": None
    }

    # Determine start station
    if from_area:
        # User is starting from an area without direct train access
        result["first_mile"] = {
            "area": from_area["area_name"],
            "connections": from_area["nearest_stations"]
        }
        # Use first station as train start
        start_station = from_area["nearest_stations"][0]["station"]
    else:
        start_station = from_place

    # Determine end station
    if to_area:
        # User's destination is an area without direct train access
        result["last_mile"] = {
            "area": to_area["area_name"],
            "connections": to_area["nearest_stations"]
        }
        # Use first station as train end
        end_station = to_area["nearest_stations"][0]["station"]
    else:
        end_station = to_place

    # Get train route
    if train_route_func:
        result["train_route"] = train_route_func(start_station, end_station)

    return result


def format_combined_route(result):
    """Format combined route for display."""
    response = ""

    # First mile (bus to station)
    if result.get("first_mile"):
        fm = result["first_mile"]
        conn = fm["connections"][0]  # Primary connection
        response += f"**Step 1: Bus from {fm['area']}**\n"
        response += f"Take Bus {' or '.join(conn['buses'])} to {conn['station']} Station\n"
        response += f"({conn['travel_time']})\n\n"

    # Train route
    if result.get("train_route"):
        step = 2 if result.get("first_mile") else 1
        response += f"**Step {step}: Train**\n"
        response += result["train_route"] + "\n\n"

    # Last mile (station to destination)
    if result.get("last_mile"):
        lm = result["last_mile"]
        conn = lm["connections"][0]
        step = 3 if result.get("first_mile") and result.get("train_route") else 2
        response += f"**Step {step}: Bus to {lm['area']}**\n"
        response += f"From {conn['station']} take Bus {' or '.join(conn['buses'])}\n"
        response += f"({conn['travel_time']})\n"

    return response


# Quick lookup for chatbot
def check_needs_bus_connection(query):
    """Check if query mentions an area that needs bus connection."""
    query_lower = query.lower()

    for area_key, area_data in FIRST_LAST_MILE.items():
        for keyword in area_data["keywords"]:
            if keyword in query_lower:
                return True, area_key, area_data

    return False, None, None


# ==================================================
# TEST
# ==================================================
if __name__ == "__main__":
    print("First/Last Mile Bus Connections")
    print("=" * 50)

    # Test queries
    test_queries = [
        "Powai to Churchgate",
        "Juhu beach to Dadar",
        "How to reach BKC",
        "Nariman Point to Thane"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        needs_bus, area_key, area_data = check_needs_bus_connection(query)
        if needs_bus:
            print(f"Area found: {area_data['area_name']}")
            print(format_bus_response(area_data))
        else:
            print("Direct train route available")
