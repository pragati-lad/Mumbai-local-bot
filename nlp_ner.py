# ==================================================
# Named Entity Recognition for Mumbai Local Chatbot
# ==================================================
# Station extraction using spaCy PhraseMatcher
# Time extraction with natural language support
# Falls back to existing difflib fuzzy matching
# ==================================================

import re
from datetime import datetime
from difflib import get_close_matches

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    nlp = spacy.blank("en")
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None

# Import station lists from existing module
from train_chatbot_enhanced import ALL_STATIONS

# Abbreviations and common misspellings -> canonical name
STATION_ALIASES = {
    "cst": "CSMT", "csmt": "CSMT", "vt": "CSMT",
    "victoria terminus": "CSMT", "chhatrapati shivaji": "CSMT",
    "mumbai cst": "CSMT", "cstm": "CSMT",
    "anderi": "Andheri", "andhery": "Andheri", "andehri": "Andheri",
    "borivli": "Borivali", "borivilli": "Borivali",
    "dombivali": "Dombivli", "dombivili": "Dombivli",
    "ghatkopr": "Ghatkopar",
    "churchgte": "Churchgate", "chruchgate": "Churchgate",
    "curla": "Kurla",
    "thana": "Thane", "thanae": "Thane",
    "kalian": "Kalyan", "kalyaan": "Kalyan",
    "panwel": "Panvel",
    "vasai": "Vasai Road",
    "nallasopara": "Nalla Sopara", "nala sopara": "Nalla Sopara",
    "nalasopara": "Nalla Sopara",
    "khar": "Khar Road",
    "bombay central": "Mumbai Central",
    "marine line": "Marine Lines",
    "mahim": "Mahim Junction",
    "belapur cbd": "Belapur", "cbd belapur": "Belapur",
    "miraroad": "Mira Road",
    "bhayander": "Bhayandar",
    "dahiser": "Dahisar",
    "vileparle": "Vile Parle", "parle": "Vile Parle",
}

# Natural time expressions
TIME_EXPRESSIONS = {
    "morning": "08:00",
    "early morning": "06:00",
    "subah": "08:00",
    "afternoon": "13:00",
    "dopahar": "13:00",
    "evening": "17:30",
    "shaam": "17:30",
    "night": "21:00",
    "raat": "21:00",
    "rush hour": "08:30",
    "peak time": "08:30",
    "peak hour": "08:30",
    "off peak": "13:00",
    "lunch time": "12:30",
    "late night": "22:30",
}

# Build PhraseMatcher
_station_matcher = None


def _build_phrase_matcher():
    if nlp is None:
        return None
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(station.lower()) for station in ALL_STATIONS]
    matcher.add("STATION", patterns)
    alias_patterns = [nlp.make_doc(alias.lower()) for alias in STATION_ALIASES.keys()]
    matcher.add("STATION_ALIAS", alias_patterns)
    return matcher


def _get_station_matcher():
    global _station_matcher
    if _station_matcher is None:
        _station_matcher = _build_phrase_matcher()
    return _station_matcher


def extract_stations_nlp(query):
    """
    Extract station names from query using spaCy PhraseMatcher.
    Falls back to difflib fuzzy matching for unrecognized tokens.
    Returns list of canonical station names.
    """
    if nlp is None:
        return _extract_stations_fallback(query)

    doc = nlp(query.lower())
    matcher = _get_station_matcher()
    if matcher is None:
        return _extract_stations_fallback(query)

    found_stations = []
    found_spans = []

    # Phase 1: PhraseMatcher for exact/alias matches
    matches = matcher(doc)
    for match_id, start, end in matches:
        span_text = doc[start:end].text.lower()
        label = nlp.vocab.strings[match_id]

        if label == "STATION_ALIAS":
            canonical = STATION_ALIASES.get(span_text)
        else:
            canonical = None
            for s in ALL_STATIONS:
                if s.lower() == span_text:
                    canonical = s
                    break

        if canonical and canonical not in found_stations:
            found_stations.append(canonical)
            found_spans.append((start, end))

    # Phase 2: Fuzzy fallback for unmatched words
    if len(found_stations) < 2:
        ignore_words = {
            'train', 'trains', 'from', 'to', 'the', 'a', 'an', 'on', 'at',
            'line', 'local', 'fast', 'slow', 'ac', 'next', 'show', 'get',
            'western', 'central', 'harbour', 'harbor', 'railway',
            'fare', 'price', 'cost', 'ticket', 'kitna', 'rate', 'charge',
            'how', 'much', 'what', 'is', 'for', 'between', 'after',
            'before', 'around', 'about', 'please', 'tell', 'me',
            'morning', 'evening', 'night', 'afternoon', 'peak', 'rush',
            'all', 'schedule', 'full', 'time', 'timing', 'timings',
            'am', 'pm', 'platform', 'info', 'review', 'reviews'
        }

        covered_indices = set()
        for start, end in found_spans:
            for i in range(start, end):
                covered_indices.add(i)

        for token in doc:
            if token.i in covered_indices:
                continue
            if token.text.lower() in ignore_words:
                continue
            if len(token.text) < 3:
                continue

            match = get_close_matches(token.text, ALL_STATIONS, n=1, cutoff=0.6)
            if match and match[0] not in found_stations:
                found_stations.append(match[0])

    return found_stations


def _extract_stations_fallback(query):
    """Original difflib-based extraction."""
    from train_chatbot_enhanced import extract_stations
    return extract_stations(query)


def extract_time_nlp(query):
    """
    Extract time from query. Handles:
    - Natural expressions: "evening", "rush hour", "morning"
    - Explicit times: "at 5pm", "3:30 pm", "14:00"
    - Approximate: "around 5", "after 6"
    Returns datetime.time or None.
    """
    q = query.lower().strip()

    # Phase 1: Natural time expressions
    for expression, time_str in sorted(TIME_EXPRESSIONS.items(), key=lambda x: -len(x[0])):
        if expression in q:
            hour, minute = map(int, time_str.split(":"))
            return datetime.strptime(f"{hour}:{minute}", "%H:%M").time()

    # Phase 2: Existing regex patterns
    from train_chatbot_enhanced import extract_time_from_query
    result = extract_time_from_query(query)
    if result:
        return result

    # Phase 3: Bare number with context
    bare_pattern = r'(?:around|after|by|before)\s+(\d{1,2})(?!\s*[:]\d)'
    match = re.search(bare_pattern, q)
    if match:
        hour = int(match.group(1))
        if 1 <= hour <= 12:
            if any(w in q for w in ["morning", "subah", "early"]):
                pass
            else:
                hour = hour + 12 if hour != 12 else 12
            try:
                return datetime.strptime(f"{hour}:00", "%H:%M").time()
            except ValueError:
                pass

    return None
