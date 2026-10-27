# Multilingual Hate Speech Detection System

End-to-end desktop application to detect hate speech from text and images with multilingual support.

### What is this project?
User writes text or uploads image -> App detects language -> Translates to English -> Checks if text is Hate Speech, Sarcasm, and Sentiment -> Saves result in database. Full login/register system with history page.

### What is used?

**Languages & Libraries:**
- Python, Tkinter (GUI)
- Scikit-learn: TfidfVectorizer (max_features=3000), LogisticRegression
- NLTK VADER (sentiment)
- Pillow, pytesseract (OCR for images)
- langdetect, deep-translator, argostranslate (language detection + translation)
- mysql-connector-python (database)
- joblib (save models)

**Models:**
1. Hate Speech Model: Trained on labeled_data.csv (24,783 tweets) -> 92.20% Accuracy
2. Sarcasm Model: Trained on Sarcasm_Headlines_Dataset + v2 (55,328 headlines) -> 87.72% Accuracy

**Files:**
- homepage.py - Main GUI (Login, Register, Text Detection, Image Detection, History)
- detection_module.py - Core logic (translation + prediction)
- detection_image.py - Extract text from images using Tesseract OCR
- db.py - MySQL tables creation (users, text_submissions, image_submissions)
- storage.py - Save uploaded images & thumbnails
- train_hate.py - Training script for hate speech model
- train_sarcasm.py - Training script for sarcasm model
- prepare_sarcasm.py - Combine 2 JSON files to CSV

### How to Run?
1. pip install -r requirements.txt
2. Install MySQL and create database
3. Install Tesseract OCR
4. python homepage.py

### Results:
- Hate Speech: 92.2% Accuracy
- Sarcasm: 87.7% Accuracy

### Publication:
IJEDR Journal, Dec 2025, Paper ID: IJEDR2504757


