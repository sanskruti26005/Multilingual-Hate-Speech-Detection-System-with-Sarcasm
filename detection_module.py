# detection_module.py
import joblib
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# -------------------
# Load hate speech model
# -------------------
hate_model = joblib.load("text_hate_model.joblib")  # use your correct filename
hate_vectorizer = joblib.load("text_hate_vectorizer.joblib")

# -------------------
# Load sarcasm model
# -------------------
sarcasm_model = joblib.load("sarcasm_model.joblib")
sarcasm_vectorizer = joblib.load("sarcasm_vectorizer.joblib")

# -------------------
# NLTK Sentiment Analyzer
# -------------------
sia = SentimentIntensityAnalyzer()


def detect_hate_speech(text, source_lang="auto"):
    """
    Returns a dictionary:
    {
        "predicted_label": str,
        "score": float,
        "sentiment": str,
        "sarcasm": "Detected" | "Not Detected"
    }
    """
    if not text.strip():
        return {
            "predicted_label": "Empty Text",
            "score": 0.0,
            "sentiment": "Neutral",
            "sarcasm": "Not Detected"
        }

    # --- Hate speech prediction ---
    try:
        vec = hate_vectorizer.transform([text])
        pred_label = hate_model.predict(vec)[0]
        score = max(hate_model.predict_proba(vec)[0])
    except Exception as e:
        pred_label = "Error"
        score = 0.0

    # --- Sarcasm prediction ---
    try:
        vec_s = sarcasm_vectorizer.transform([text])
        pred_sarcasm = sarcasm_model.predict(vec_s)[0]
        sarcasm_label = "Detected" if pred_sarcasm == 1 else "Not Detected"
    except Exception:
        sarcasm_label = "Not Detected"

    # --- Sentiment ---
    try:
        sentiment_score = sia.polarity_scores(text)["compound"]
        if sentiment_score >= 0.05:
            sentiment = "Positive"
        elif sentiment_score <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
    except Exception:
        sentiment = "Neutral"

    return {
        "predicted_label": str(pred_label),
        "score": float(score),
        "sentiment": sentiment,
        "sarcasm": sarcasm_label
    }
