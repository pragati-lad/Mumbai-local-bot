# ==================================================
# Hindi/Marathi Language Support for Mumbai Local Bot
# ==================================================

# Common Hindi/Marathi words mapped to English equivalents
HINDI_KEYWORDS = {
    # Stations
    "se": "from",
    "tak": "to",
    "jana": "to",
    "jaana": "to",
    "kaise": "how",
    "kab": "when",

    # Train related
    "gaadi": "train",
    "gadi": "train",
    "train": "train",
    "local": "local",
    "fast": "fast",
    "slow": "slow",

    # Time
    "subah": "morning",
    "dopahar": "afternoon",
    "shaam": "evening",
    "raat": "night",
    "baje": "o'clock",

    # Questions
    "kitna": "how much",
    "kitne": "how much",
    "kahan": "where",
    "kaun": "which",
    "konsa": "which",

    # Fare
    "kiraya": "fare",
    "paisa": "money",
    "ticket": "ticket",

    # Platform
    "platform": "platform",
    "number": "number",

    # Common phrases
    "chalti": "running",
    "aati": "coming",
    "milegi": "available",
    "hai": "is",
    "hain": "are",
    "ka": "of",
    "ki": "of",
    "ke": "of",
    "me": "in",
    "pe": "at",
    "par": "on",
}

# Marathi keywords
MARATHI_KEYWORDS = {
    # Stations
    "pasun": "from",
    "la": "to",
    "kadhe": "to",

    # Questions
    "kiti": "how much",
    "kuthe": "where",
    "kasa": "how",
    "kaisa": "how",
    "konti": "which",

    # Train
    "gaadi": "train",
    "local": "local",

    # Time
    "sakali": "morning",
    "dupari": "afternoon",
    "sandhyakali": "evening",
    "ratri": "night",

    # Common
    "aahe": "is",
    "asel": "will be",
    "platform": "platform",
    "bhada": "fare",
}

# Response templates in Hindi
HINDI_RESPONSES = {
    "welcome": "Mumbai Local Bot mein aapka swagat hai! Main train timing, routes aur fare mein madad kar sakta hoon.",
    "no_trains": "Koi train nahi mili. Kripya station ka naam check karein.",
    "platform_prompt": "Konse station ka platform chahiye?",
    "fare_prompt": "Kahan se kahan ka fare chahiye?",
}

# Response templates in Marathi
MARATHI_RESPONSES = {
    "welcome": "Mumbai Local Bot madhe tumcha swagat aahe! Mi train timing, routes ani fare madhe madad karu shakto.",
    "no_trains": "Train sapadli nahi. Krupaya station che naav tapasa.",
    "platform_prompt": "Kontya station cha platform pahije?",
    "fare_prompt": "Kuthun kuthe fare pahije?",
}


def detect_language(query):
    """Detect if query is in Hindi/Marathi or English."""
    q_lower = query.lower()
    words = q_lower.split()

    hindi_count = sum(1 for w in words if w in HINDI_KEYWORDS)
    marathi_count = sum(1 for w in words if w in MARATHI_KEYWORDS)

    if hindi_count >= 2:
        return "hindi"
    elif marathi_count >= 2:
        return "marathi"
    return "english"


def normalize_query(query):
    """Convert Hindi/Marathi query to English equivalent."""
    q_lower = query.lower()
    words = q_lower.split()

    # Replace Hindi/Marathi words with English
    normalized = []
    for word in words:
        if word in HINDI_KEYWORDS:
            normalized.append(HINDI_KEYWORDS[word])
        elif word in MARATHI_KEYWORDS:
            normalized.append(MARATHI_KEYWORDS[word])
        else:
            normalized.append(word)

    return " ".join(normalized)


def get_response_template(key, language="english"):
    """Get response template in appropriate language."""
    if language == "hindi" and key in HINDI_RESPONSES:
        return HINDI_RESPONSES[key]
    elif language == "marathi" and key in MARATHI_RESPONSES:
        return MARATHI_RESPONSES[key]
    return None


# Common phrases to detect intent
INTENT_PATTERNS = {
    "fare": ["kitna kiraya", "ticket kitna", "fare kitna", "kiti bhada", "kiti paisa"],
    "platform": ["konsa platform", "platform number", "konti platform"],
    "timing": ["kab hai", "kitne baje", "kiti vajta", "train kab"],
    "route": ["kaise jaye", "kasa jaaycha", "route batao"],
}


def detect_intent_from_hindi(query):
    """Detect intent from Hindi/Marathi query."""
    q_lower = query.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in q_lower:
                return intent

    return None
