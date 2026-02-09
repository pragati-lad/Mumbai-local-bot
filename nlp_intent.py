# ==================================================
# Intent Classification for Mumbai Local Train Chatbot
# ==================================================
# TF-IDF + Logistic Regression trained on labeled examples
# Falls back to keyword matching if model unavailable
# ==================================================

import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "intent_model.pkl")
CONFIDENCE_THRESHOLD = 0.45

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        return _model
    except Exception as e:
        print(f"Warning: Could not load intent model: {e}")
        return None


def classify_intent(query):
    """
    Classify user query into one of 11 intents.
    Returns (intent_name, confidence) or ("unknown", 0.0).
    """
    model = _load_model()
    if model is None:
        return ("unknown", 0.0)

    q = query.lower().strip()
    probabilities = model.predict_proba([q])[0]
    max_idx = probabilities.argmax()
    confidence = probabilities[max_idx]
    intent = model.classes_[max_idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return ("unknown", confidence)

    return (intent, confidence)


def get_all_intents(query):
    """Get all intents sorted by confidence (for debugging)."""
    model = _load_model()
    if model is None:
        return []

    q = query.lower().strip()
    probabilities = model.predict_proba([q])[0]
    intents = list(zip(model.classes_, probabilities))
    intents.sort(key=lambda x: x[1], reverse=True)
    return intents
