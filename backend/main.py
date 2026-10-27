import requests
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

@app.route("/api/creators")
def creators():
    path = BASE_DIR / "data" / "demo" / "beauty_creators.csv"
    df = pd.read_csv(path)
    return jsonify(df.to_dict(orient="records"))

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

    return jsonify({
        "total_influencers": len(df),
        "average_followers": round(float(df["followers"].mean())),
        "top_categories": (
            df["category_1"].value_counts().head(10).to_dict()
        )
    })

@app.route("/api/scrape", methods=["POST"])
def scrape():
    try:
        records = scrape_quotes()
        return jsonify({
            "status": "success",
            "count": len(records),
            "preview": records[:5]
        })
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": str(exc)}), 502

if __name__ == "__main__":
    app.run(debug=True)
