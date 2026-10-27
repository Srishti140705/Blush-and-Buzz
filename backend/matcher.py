
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "demo" / "beauty_creators.csv"

def find_matches(niche, budget, audience, location=None):
    df = pd.read_csv(DATA_FILE)
    results = []

    for _, creator in df.iterrows():
        fee = float(creator["estimated_fee"])

        # Budget is a hard requirement
        if fee > budget:
            continue

        score = 0
        reasons = []

        # Niche match: 40 points
        if str(creator["niche"]).lower() == niche.lower():
            score += 40
            reasons.append("Creator specializes in your selected niche")

        # Audience match: 25 points
        if str(creator["audience"]) == audience:
            score += 25
            reasons.append("Matches your target age group")

        # Engagement: up to 20 points
        engagement = float(creator["engagement_rate"])
        score += min(20, engagement / 6 * 20)
        reasons.append(f"{engagement:.1f}% demo engagement rate")

        # Location match: 10 points
        if location and str(creator["location"]).lower() == location.lower():
            score += 10
            reasons.append("Matches your target location")

        # Budget efficiency: 5 points
        if fee <= budget * 0.75:
            score += 5
            reasons.append("Comfortably within campaign budget")

        results.append({
            **creator.to_dict(),
            "match_score": round(score, 1),
            "reasons": reasons
        })

    return sorted(
        results,
        key=lambda x: x["match_score"],
        reverse=True
    )

if __name__ == "__main__":
    matches = find_matches(
        niche="Makeup",
        budget=30000,
        audience="18-24",
        location="India"
    )

    for creator in matches[:5]:
        print(f"\n{creator['name']}: {creator['match_score']}/100")
        for reason in creator["reasons"]:
            print("-", reason)
