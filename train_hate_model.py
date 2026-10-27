import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("labeled_data.csv")

X = df["tweet"]          # your text column
y = df["class"]          # your label column

vectorizer = TfidfVectorizer(max_features=3000)
X_vec = vectorizer.fit_transform(X)

model = LogisticRegression()
model.fit(X_vec, y)

joblib.dump(model, "text_hate_model.joblib")
joblib.dump(vectorizer, "text_hate_vectorizer.joblib")

print("✅ Hate speech model trained & saved")
