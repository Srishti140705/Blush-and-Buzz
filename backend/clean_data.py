
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "instagram_raw.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "instagram_cleaned.csv"

def convert_number(value):
    if pd.isna(value):
        return None

    text = str(value).strip().upper().replace(",", "")

    try:
        if text.endswith("M"):
            return float(text[:-1]) * 1_000_000
        if text.endswith("K"):
            return float(text[:-1]) * 1_000
        if text.endswith("B"):
            return float(text[:-1]) * 1_000_000_000
        return float(text)
    except ValueError:
        return None

df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# Standardize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", "_", regex=True)
    .str.replace(r"[^\w]", "", regex=True)
)

df = df.rename(columns={
    "influencer_insta_name": "username",
    "instagram_name": "display_name",
    "audience_countrymostly": "audience_country",
    "authentic_engagement": "authentic_engagement",
    "engagement_avg": "average_engagement"
})

# Clean text fields
for col in ["display_name", "category_1", "category_2", "audience_country"]:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()

df["username"] = df["username"].astype(str).str.strip()

# Convert follower and engagement counts
for col in ["followers", "authentic_engagement", "average_engagement"]:
    df[col] = df[col].apply(convert_number)

# Calculate engagement percentage
df["engagement_rate"] = (
    df["average_engagement"] / df["followers"] * 100
).round(2)

df["engagement_rate"] = df["engagement_rate"].replace(
    [float("inf"), float("-inf")], float("nan")
)

# Remove duplicate usernames
df = df.drop_duplicates(subset=["username"])

# Remove rows without valid follower counts
df = df.dropna(subset=["followers"])
df = df[df["followers"] > 0]

# Save cleaned data
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("DATA CLEANING COMPLETE!")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())
print("Saved to:", OUTPUT_FILE)
print(df.head().to_string(index=False))
