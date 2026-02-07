# ==================================================
# Mumbai Local Train Fare Calculator
# ==================================================
# Distance-based fare calculation for Mumbai suburban trains
# ==================================================

# Fare slabs (in Rs) - Updated 2024
# Based on Indian Railways suburban fare structure

FARE_SLABS = {
    # Distance (km): (Second Class, First Class, AC)
    (0, 5): (5, 45, 60),
    (5, 10): (5, 55, 70),
    (10, 15): (10, 70, 85),
    (15, 20): (10, 85, 100),
    (20, 25): (15, 105, 120),
    (25, 30): (15, 120, 140),
    (30, 35): (20, 140, 160),
    (35, 40): (20, 160, 180),
    (40, 45): (25, 180, 200),
    (45, 50): (25, 195, 220),
    (50, 60): (30, 215, 250),
    (60, 70): (30, 230, 280),
    (70, 80): (35, 245, 305),
    (80, 100): (35, 260, 330),
}

# Monthly pass multiplier (approx 15 days fare for unlimited travel)
MONTHLY_PASS_MULTIPLIER = {
    "second": 15,
    "first": 15,
    "ac": 20  # AC passes are relatively more expensive
}

# Distance between stations (in km) - Key routes
# Format: (Station1, Station2): distance_km
STATION_DISTANCES = {
    # Western Line (Churchgate to Virar)
    ("Churchgate", "Marine Lines"): 1.5,
    ("Churchgate", "Charni Road"): 2.5,
    ("Churchgate", "Grant Road"): 3.5,
    ("Churchgate", "Mumbai Central"): 4.5,
    ("Churchgate", "Mahalakshmi"): 6,
    ("Churchgate", "Lower Parel"): 7,
    ("Churchgate", "Prabhadevi"): 8,
    ("Churchgate", "Dadar"): 9,
    ("Churchgate", "Mahim"): 10,
    ("Churchgate", "Bandra"): 12,
    ("Churchgate", "Khar Road"): 14,
    ("Churchgate", "Santacruz"): 15,
    ("Churchgate", "Vile Parle"): 17,
    ("Churchgate", "Andheri"): 19,
    ("Churchgate", "Jogeshwari"): 21,
    ("Churchgate", "Goregaon"): 24,
    ("Churchgate", "Malad"): 27,
    ("Churchgate", "Kandivali"): 30,
    ("Churchgate", "Borivali"): 33,
    ("Churchgate", "Dahisar"): 37,
    ("Churchgate", "Mira Road"): 41,
    ("Churchgate", "Bhayandar"): 44,
    ("Churchgate", "Vasai Road"): 52,
    ("Churchgate", "Nalla Sopara"): 56,
    ("Churchgate", "Virar"): 60,

    # Central Line (CSMT to Kasara/Karjat)
    ("CSMT", "Masjid"): 1.5,
    ("CSMT", "Byculla"): 4,
    ("CSMT", "Chinchpokli"): 5,
    ("CSMT", "Currey Road"): 6,
    ("CSMT", "Parel"): 7,
    ("CSMT", "Dadar"): 9,
    ("CSMT", "Matunga"): 11,
    ("CSMT", "Sion"): 13,
    ("CSMT", "Kurla"): 15,
    ("CSMT", "Vidyavihar"): 17,
    ("CSMT", "Ghatkopar"): 18,
    ("CSMT", "Vikhroli"): 21,
    ("CSMT", "Kanjurmarg"): 23,
    ("CSMT", "Bhandup"): 25,
    ("CSMT", "Nahur"): 27,
    ("CSMT", "Mulund"): 29,
    ("CSMT", "Thane"): 34,
    ("CSMT", "Kalwa"): 37,
    ("CSMT", "Dombivli"): 48,
    ("CSMT", "Kalyan"): 54,
    ("CSMT", "Ambernath"): 62,
    ("CSMT", "Badlapur"): 68,
    ("CSMT", "Kasara"): 121,
    ("CSMT", "Karjat"): 101,

    # Harbour Line (CSMT to Panvel)
    ("CSMT", "Sandhurst Road"): 2,
    ("CSMT", "Dockyard Road"): 3,
    ("CSMT", "Sewri"): 5,
    ("CSMT", "Vadala Road"): 7,
    ("CSMT", "GTB Nagar"): 9,
    ("CSMT", "Chunabhatti"): 11,
    ("CSMT", "Chembur"): 14,
    ("CSMT", "Govandi"): 16,
    ("CSMT", "Mankhurd"): 19,
    ("CSMT", "Vashi"): 25,
    ("CSMT", "Sanpada"): 27,
    ("CSMT", "Nerul"): 32,
    ("CSMT", "Belapur"): 35,
    ("CSMT", "Panvel"): 42,

    # Key interchange distances
    ("Dadar", "Thane"): 25,
    ("Dadar", "Borivali"): 24,
    ("Dadar", "Andheri"): 10,
    ("Dadar", "Churchgate"): 9,
    ("Dadar", "CSMT"): 9,
    ("Dadar", "Kurla"): 6,
    ("Dadar", "Bandra"): 3,
    ("Dadar", "Panvel"): 33,

    ("Kurla", "Thane"): 19,
    ("Kurla", "CSMT"): 15,
    ("Kurla", "Panvel"): 27,
    ("Kurla", "Vashi"): 10,
    ("Kurla", "Ghatkopar"): 3,
    ("Kurla", "Andheri"): 8,

    ("Thane", "Kalyan"): 20,
    ("Thane", "Dombivli"): 14,
    ("Thane", "Panvel"): 24,
    ("Thane", "Vashi"): 11,

    ("Bandra", "Andheri"): 7,
    ("Bandra", "Borivali"): 21,
    ("Bandra", "Churchgate"): 12,
    ("Bandra", "Dadar"): 3,
    ("Bandra", "Kurla"): 4,

    ("Andheri", "Borivali"): 14,
    ("Andheri", "Virar"): 41,
    ("Andheri", "Churchgate"): 19,
    ("Andheri", "Ghatkopar"): 7,  # Via Metro

    ("Borivali", "Virar"): 27,
    ("Borivali", "Churchgate"): 33,

    ("Vashi", "Panvel"): 17,
    ("Vashi", "Belapur"): 10,
    ("Vashi", "CSMT"): 25,

    ("Ghatkopar", "Thane"): 16,
    ("Ghatkopar", "CSMT"): 18,
    ("Ghatkopar", "Andheri"): 7,  # Via Metro
    ("Ghatkopar", "Panvel"): 24,

    # More Harbour Line
    ("Panvel", "Vashi"): 17,
    ("Panvel", "Belapur"): 7,
    ("Panvel", "Nerul"): 10,
    ("Panvel", "CSMT"): 42,
    ("Panvel", "Kurla"): 27,
}


def get_distance(station1, station2):
    """Get distance between two stations."""
    # Normalize station names
    s1 = normalize_station(station1)
    s2 = normalize_station(station2)

    if s1.lower() == s2.lower():
        return 0

    # Build lowercase lookup for case-insensitive matching
    distance_lookup = {}
    for (a, b), dist in STATION_DISTANCES.items():
        distance_lookup[(a.lower(), b.lower())] = dist
        distance_lookup[(b.lower(), a.lower())] = dist

    # Check direct distance
    key = (s1.lower(), s2.lower())
    if key in distance_lookup:
        return distance_lookup[key]

    # Try to calculate via common interchange
    for interchange in ["Dadar", "Kurla", "Thane", "Bandra", "Andheri", "CSMT", "Churchgate"]:
        key1 = (s1.lower(), interchange.lower())
        key2 = (interchange.lower(), s2.lower())

        if key1 in distance_lookup and key2 in distance_lookup:
            return distance_lookup[key1] + distance_lookup[key2]

    return None


def normalize_station(station):
    """Normalize station name for matching."""
    station = station.strip()

    # Common aliases (case-insensitive)
    aliases = {
        "cst": "CSMT",
        "csmt": "CSMT",
        "vt": "CSMT",
        "victoria terminus": "CSMT",
        "chhatrapati shivaji": "CSMT",
        "bombay central": "Mumbai Central",
        "parle": "Vile Parle",
        "cbd belapur": "Belapur",
        "cbd": "Belapur",
        "nallasopara": "Nalla Sopara",
        "vasai": "Vasai Road",
    }

    station_lower = station.lower()
    if station_lower in aliases:
        return aliases[station_lower]

    # Title case for other stations
    return station.title()


def get_fare(distance_km):
    """Get fare for given distance."""
    if distance_km is None:
        return None

    for (min_km, max_km), (second, first, ac) in FARE_SLABS.items():
        if min_km <= distance_km < max_km:
            return {
                "second_class": second,
                "first_class": first,
                "ac": ac
            }

    # For distances beyond 100km
    if distance_km >= 100:
        return {
            "second_class": 40,
            "first_class": 280,
            "ac": 360
        }

    return None


def calculate_fare(station1, station2):
    """Calculate fare between two stations."""
    distance = get_distance(station1, station2)

    if distance is None:
        return None

    fares = get_fare(distance)

    if fares is None:
        return None

    return {
        "from": normalize_station(station1),
        "to": normalize_station(station2),
        "distance_km": round(distance, 1),
        "fares": fares,
        "monthly_pass": {
            "second_class": fares["second_class"] * MONTHLY_PASS_MULTIPLIER["second"],
            "first_class": fares["first_class"] * MONTHLY_PASS_MULTIPLIER["first"],
            "ac": fares["ac"] * MONTHLY_PASS_MULTIPLIER["ac"]
        }
    }


def format_fare_response(fare_data):
    """Format fare data for chatbot response."""
    if fare_data is None:
        return None

    f = fare_data["fares"]
    m = fare_data["monthly_pass"]

    response = f"""
**Fare: {fare_data['from']} to {fare_data['to']}**
Distance: {fare_data['distance_km']} km

| Class | Single | Monthly Pass |
|-------|--------|--------------|
| Second Class | Rs {f['second_class']} | Rs {m['second_class']} |
| First Class | Rs {f['first_class']} | Rs {m['first_class']} |
| AC Local | Rs {f['ac']} | Rs {m['ac']} |

_Fares are approximate. Check UTS app for exact prices._
"""
    return response


# ==================================================
# TEST
# ==================================================
if __name__ == "__main__":
    print("Mumbai Local Train Fare Calculator")
    print("=" * 50)

    test_routes = [
        ("Churchgate", "Andheri"),
        ("Dadar", "Thane"),
        ("CSMT", "Panvel"),
        ("Bandra", "Borivali"),
        ("Andheri", "Virar"),
    ]

    for src, dst in test_routes:
        print(f"\n{src} to {dst}:")
        result = calculate_fare(src, dst)
        if result:
            print(f"  Distance: {result['distance_km']} km")
            print(f"  Second Class: Rs {result['fares']['second_class']}")
            print(f"  First Class: Rs {result['fares']['first_class']}")
            print(f"  AC: Rs {result['fares']['ac']}")
        else:
            print("  Route not found")
