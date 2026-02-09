# ==================================================
# Train Intent Classification Model
# ==================================================
# One-time script: generates intent_model.pkl
# Run: python train_intent_model.py
# ==================================================

import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def train_and_save():
    with open(os.path.join(BASE_DIR, "intent_training_data.json"), "r") as f:
        data = json.load(f)

    texts = []
    labels = []
    for intent, examples in data.items():
        for example in examples:
            texts.append(example.lower())
            labels.append(intent)

    print(f"Training on {len(texts)} examples across {len(data)} intents")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            strip_accents="unicode"
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=5.0,
            solver="lbfgs"
        ))
    ])

    pipeline.fit(texts, labels)

    scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    print(f"Cross-validation accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")

    model_path = os.path.join(BASE_DIR, "intent_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"Model saved to {model_path}")
    print(f"Model size: {os.path.getsize(model_path) / 1024:.1f} KB")


if __name__ == "__main__":
    train_and_save()
