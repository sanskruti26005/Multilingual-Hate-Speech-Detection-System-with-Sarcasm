import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("sarcasm.csv")

X = df["text"]
y = df["label"]

vectorizer = TfidfVectorizer(max_features=3000)
X_vec = vectorizer.fit_transform(X)

model = LogisticRegression()
model.fit(X_vec, y)

joblib.dump(model, "sarcasm_model.joblib")
joblib.dump(vectorizer, "sarcasm_vectorizer.joblib")

print("✅ Sarcasm model trained & saved")
