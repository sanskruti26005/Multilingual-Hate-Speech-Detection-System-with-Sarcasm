import pandas as pd

# Load both JSON files
df1 = pd.read_json("Sarcasm_Headlines_Dataset.json", lines=True)
df2 = pd.read_json("Sarcasm_Headlines_Dataset_v2.json", lines=True)

# Combine them
df = pd.concat([df1, df2], ignore_index=True)

# Keep only relevant columns and rename
df = df.rename(columns={"headline": "text", "is_sarcastic": "label"})
df = df[["text", "label"]]

# Save as CSV
df.to_csv("sarcasm.csv", index=False)

print("✅ Combined sarcasm dataset saved as sarcasm.csv")
