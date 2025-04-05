import joblib
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Define paths for the model and vectorizer
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'claim_classifier_model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'tfidf_vectorizer.pkl')

# Load the pre-trained model and vectorizer
try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise RuntimeError("Model or vectorizer not found. Ensure they are trained and saved.")

def classify_claim(claim_text: str) -> tuple:
    """
    Classify the given insurance claim text into urgency and risk categories.

    Args:
        claim_text (str): The text of the insurance claim.

    Returns:
        tuple: A
