# detection_image.py
import pytesseract
from PIL import Image
from detection_module import detect_hate_speech

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def analyze_image(image_path):
    """
    Analyze image and return dictionary compatible with DB storage:
    {
        "predicted_label": str,
        "score": float,
        "extracted_text": str,
        "sentiment": str,
        "sarcasm": str
    }
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {
            "predicted_label": "Error",
            "score": 0.0,
            "extracted_text": "",
            "sentiment": "Neutral",
            "sarcasm": "Not Detected",
            "error": str(e)
        }

    # OCR text
    try:
        extracted_text = pytesseract.image_to_string(img)
    except Exception:
        extracted_text = ""

    # If OCR found text, run text detection
    if extracted_text.strip():
        res = detect_hate_speech(extracted_text)
        predicted_label = res.get("predicted_label", "Error")
        score = float(res.get("score", 0.0))
        sentiment = res.get("sentiment", "Neutral")
        sarcasm = res.get("sarcasm", "Not Detected")
    else:
        predicted_label = "No Text Detected"
        score = 0.0
        sentiment = "Neutral"
        sarcasm = "Not Detected"

    return {
        "predicted_label": predicted_label,
        "score": score,
        "extracted_text": extracted_text,
        "sentiment": sentiment,
        "sarcasm": sarcasm
    }
