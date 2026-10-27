
from pathlib import Path
import csv
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "scraped_quotes.csv"

URL = "https://quotes.toscrape.com/"

def scrape_quotes(save_csv=False):
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for quote in soup.select(".quote"):
        text = quote.select_one(".text")
        author = quote.select_one(".author")
        tags = quote.select(".tag")

        results.append({
            "quote": text.get_text(strip=True) if text else "",
            "author": author.get_text(strip=True) if author else "",
            "tags": ", ".join(tag.get_text(strip=True) for tag in tags)
        })

    if save_csv:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["quote", "author", "tags"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved to: {OUTPUT_FILE}")

    print(f"Scraped {len(results)} records")

    return results

if __name__ == "__main__":
    scrape_quotes(save_csv=True)
