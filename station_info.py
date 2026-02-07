# ==================================================
# Mumbai Station Info - Platforms, Peak Hours, Tips
# ==================================================

# Platform information for major stations
PLATFORM_INFO = {
    # Western Line
    "Churchgate": {
        "total_platforms": 4,
        "directions": {
            "Virar/Borivali": "Platform 1, 2, 3, 4",
        },
        "notes": "Terminus station - all trains start here"
    },
    "Mumbai Central": {
        "total_platforms": 4,
        "directions": {
            "Virar/Borivali": "Platform 1, 2",
            "Churchgate": "Platform 3, 4"
        }
    },
    "Dadar": {
        "total_platforms": 8,
        "directions": {
            "Virar/Borivali (Western)": "Platform 1, 2",
            "Churchgate (Western)": "Platform 3, 4",
            "Thane/Kalyan (Central)": "Platform 5, 6",
            "CSMT (Central)": "Platform 7, 8"
        },
        "notes": "Major interchange - Western & Central lines"
    },
    "Bandra": {
        "total_platforms": 5,
        "directions": {
            "Virar/Borivali": "Platform 1, 2",
            "Churchgate": "Platform 3, 4, 5"
        },
        "notes": "Harbour line trains on Platform 5"
    },
    "Andheri": {
        "total_platforms": 4,
        "directions": {
            "Virar/Borivali": "Platform 1, 2",
            "Churchgate": "Platform 3, 4"
        },
        "notes": "Metro Line 1 connects here (East side)"
    },
    "Borivali": {
        "total_platforms": 4,
        "directions": {
            "Virar": "Platform 1, 2",
            "Churchgate": "Platform 3, 4"
        }
    },

    # Central Line
    "CSMT": {
        "total_platforms": 18,
        "directions": {
            "Thane/Kalyan (Central)": "Platform 1-7",
            "Panvel (Harbour)": "Platform 8-18"
        },
        "notes": "Terminus station - all trains start here"
    },
    "Kurla": {
        "total_platforms": 6,
        "directions": {
            "Thane/Kalyan": "Platform 1, 2",
            "CSMT": "Platform 3, 4",
            "Harbour Line": "Platform 5, 6"
        },
        "notes": "Major interchange - Central & Harbour lines"
    },
    "Ghatkopar": {
        "total_platforms": 4,
        "directions": {
            "Thane/Kalyan": "Platform 1, 2",
            "CSMT": "Platform 3, 4"
        },
        "notes": "Metro Line 1 connects here"
    },
    "Thane": {
        "total_platforms": 6,
        "directions": {
            "Kalyan/Kasara/Karjat": "Platform 1, 2, 3",
            "CSMT/Dadar": "Platform 4, 5, 6"
        },
        "notes": "Trans-Harbour trains to Vashi/Panvel available"
    },
    "Kalyan": {
        "total_platforms": 8,
        "directions": {
            "Kasara": "Platform 1, 2",
            "Karjat": "Platform 3, 4",
            "CSMT/Dadar": "Platform 5, 6, 7, 8"
        },
        "notes": "Junction - trains split to Kasara/Karjat"
    },

    # Harbour Line
    "Vashi": {
        "total_platforms": 4,
        "directions": {
            "Panvel/Belapur": "Platform 1, 2",
            "CSMT/Thane": "Platform 3, 4"
        }
    },
    "Panvel": {
        "total_platforms": 4,
        "directions": {
            "CSMT": "Platform 1, 2",
            "Thane (Trans-Harbour)": "Platform 3, 4"
        },
        "notes": "Terminus station"
    }
}

# Peak hour information
PEAK_HOURS = {
    "morning": {
        "time": "8:00 AM - 10:30 AM",
        "crowd_level": "Very High",
        "tips": [
            "Trains every 3-4 mins on main lines",
            "First class less crowded but expensive",
            "Ladies coach recommended for women",
            "Avoid Dadar, Kurla, Andheri if possible"
        ]
    },
    "evening": {
        "time": "5:30 PM - 8:30 PM",
        "crowd_level": "Very High",
        "tips": [
            "Reverse direction less crowded",
            "AC locals have more space",
            "Fast trains extremely packed",
            "Consider waiting for next train"
        ]
    },
    "off_peak": {
        "time": "11:00 AM - 4:00 PM",
        "crowd_level": "Low to Medium",
        "tips": [
            "Best time to travel comfortably",
            "Seats usually available",
            "Less frequency but less crowd"
        ]
    },
    "night": {
        "time": "9:00 PM - 11:00 PM",
        "crowd_level": "Low",
        "tips": [
            "Fewer trains, check last train timing",
            "Last trains usually crowded",
            "Western last train: ~11:30 PM from Churchgate"
        ]
    }
}

# Most crowded stations
CROWDED_STATIONS = [
    "Dadar", "Kurla", "Thane", "Andheri", "Borivali",
    "Ghatkopar", "Dombivli", "Kalyan", "CSMT", "Churchgate"
]


def get_platform_info(station):
    """Get platform information for a station."""
    station_title = station.strip().title()

    # Handle aliases
    aliases = {
        "Cst": "CSMT",
        "Victoria Terminus": "CSMT",
        "Vt": "CSMT"
    }
    if station_title in aliases:
        station_title = aliases[station_title]

    return PLATFORM_INFO.get(station_title)


def format_platform_response(station):
    """Format platform info for chatbot."""
    info = get_platform_info(station)

    if not info:
        return None

    response = f"**{station.title()} Station - Platforms**\n\n"
    response += f"Total Platforms: {info['total_platforms']}\n\n"

    for direction, platforms in info['directions'].items():
        response += f"**{direction}**: {platforms}\n"

    if info.get('notes'):
        response += f"\n_{info['notes']}_"

    return response


def get_peak_hour_info():
    """Get formatted peak hour information."""
    response = "**Peak Hours - Mumbai Local**\n\n"

    response += "**Morning Rush** (8:00 - 10:30 AM)\n"
    response += "Crowd: Very High\n"
    for tip in PEAK_HOURS['morning']['tips'][:2]:
        response += f"- {tip}\n"

    response += "\n**Evening Rush** (5:30 - 8:30 PM)\n"
    response += "Crowd: Very High\n"
    for tip in PEAK_HOURS['evening']['tips'][:2]:
        response += f"- {tip}\n"

    response += "\n**Best Time**: 11 AM - 4 PM (seats available)\n"
    response += "\n_Avoid: Dadar, Kurla, Andheri during peak hours_"

    return response


# Metro Line 1 connectivity
METRO_LINE_1 = {
    "name": "Versova-Andheri-Ghatkopar (Blue Line)",
    "stations": [
        "Versova", "D N Nagar", "Azad Nagar", "Andheri",
        "Western Express Highway", "Chakala", "Airport Road",
        "Marol Naka", "Saki Naka", "Asalpha", "Jagruti Nagar", "Ghatkopar"
    ],
    "interchange": {
        "Andheri": "Western Line",
        "Ghatkopar": "Central Line"
    },
    "timings": "5:30 AM - 11:00 PM",
    "frequency": "4-8 mins",
    "fare": "Rs 10 - Rs 40"
}


def get_metro_info():
    """Get Metro Line 1 information."""
    m = METRO_LINE_1
    response = f"**Metro Line 1** - {m['name']}\n\n"
    response += f"**Stations**: {m['stations'][0]} <-> {m['stations'][-1]}\n"
    response += f"**Timings**: {m['timings']}\n"
    response += f"**Frequency**: Every {m['frequency']}\n"
    response += f"**Fare**: {m['fare']}\n\n"
    response += "**Connects to Local Trains:**\n"
    response += "- Andheri (Western Line)\n"
    response += "- Ghatkopar (Central Line)\n\n"
    response += "_Great for Versova/Airport to Central line connection!_"

    return response


def get_metro_connection(from_area, to_station):
    """Check if metro can be used for the route."""
    metro_stations = [s.lower() for s in METRO_LINE_1['stations']]

    from_lower = from_area.lower()
    to_lower = to_station.lower()

    # Check if either point is on metro
    from_on_metro = any(s in from_lower for s in metro_stations)
    to_on_metro = any(s in to_lower for s in ['andheri', 'ghatkopar'])

    if from_on_metro and to_on_metro:
        return {
            "use_metro": True,
            "from": from_area,
            "to": to_station,
            "metro_info": METRO_LINE_1
        }

    return None
