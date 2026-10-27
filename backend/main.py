import requests
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
import pandas as pd

from matcher import find_matches
from scraper import scrape_quotes

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/creator/<int:creator_id>")
def creator_profile(creator_id):
    return send_from_directory(FRONTEND_DIR, "profile.html")

@app.route("/api/creators")
def creators():
    path = BASE_DIR / "data" / "demo" / "beauty_creators.csv"
    df = pd.read_csv(path)
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/creators/<int:creator_id>")
def creator_detail(creator_id):
    path = BASE_DIR / "data" / "demo" / "beauty_creators.csv"
    df = pd.read_csv(path)
    match = df[df["creator_id"] == creator_id]
    if match.empty:
        return jsonify({"error": "Creator not found"}), 404
    return jsonify(match.iloc[0].to_dict())

@app.route("/api/match", methods=["POST"])
def match():
    data = request.get_json(silent=True) or {}

    try:
        budget = float(data.get("budget", 30000))
        if budget <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Enter a valid positive budget"}), 400

    matches = find_matches(
        niche=str(data.get("niche", "Makeup")),
        budget=budget,
        audience=str(data.get("audience", "18-24")),
        location=data.get("location")
    )
    return jsonify(matches)

@app.route("/api/analytics")
def analytics():
    path = BASE_DIR / "data" / "processed" / "instagram_cleaned.csv"
    df = pd.read_csv(path)

    df["followers"] = pd.to_numeric(df["followers"], errors="coerce")
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce")
    df["category_1"] = df["category_1"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")

    category_counts = df["category_1"].value_counts().head(10)
    valid_engagement = df[df["engagement_rate"].notna() & df["engagement_rate"].between(0, 100)]
    category_engagement = (
        valid_engagement.groupby("category_1")["engagement_rate"]
        .agg(["mean", "count"])
        .query("count >= 3")
        .sort_values("mean", ascending=False)
        .head(10)
        .sort_values("mean")
    )
    scatter = df[
        df["followers"].notna()
        & (df["followers"] > 0)
        & df["engagement_rate"].notna()
        & df["engagement_rate"].between(0, 25)
    ][["followers", "engagement_rate", "category_1"]]
    if len(scatter) > 300:
        scatter = scatter.sample(300, random_state=42)

    return jsonify({
        "total_influencers": int(len(df)),
        "average_followers": round(float(df["followers"].mean())),
        "average_engagement_rate": round(float(valid_engagement["engagement_rate"].mean()), 2),
        "most_represented_category": str(category_counts.index[0]),
        "top_categories": category_counts.to_dict(),
        "category_distribution": {
            "labels": category_counts.index.tolist(),
            "values": [int(value) for value in category_counts.values]
        },
        "engagement_by_category": {
            "labels": category_engagement.index.tolist(),
            "values": [round(float(value), 2) for value in category_engagement["mean"].values]
        },
        "followers_vs_engagement": {
            "followers": [float(value) for value in scatter["followers"].values],
            "engagement_rate": [float(value) for value in scatter["engagement_rate"].values],
            "categories": scatter["category_1"].tolist()
        }
    })

@app.route("/api/scrape", methods=["POST"])
def scrape():
    try:
        records = scrape_quotes()
        return jsonify({
            "status": "success",
            "count": len(records),
            "preview": records[:5],
            "records": records
        })
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc)}), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
