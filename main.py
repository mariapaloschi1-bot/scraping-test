import requests
import pandas as pd
import json
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import os

# ======================
# LOAD ENV
# ======================

load_dotenv()

LOGIN = os.getenv("DATAFORSEO_LOGIN")
PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

# ======================
# READ KEYWORDS
# ======================

with open("keywords.txt", "r", encoding="utf-8") as f:
    keywords = [k.strip() for k in f.readlines() if k.strip()]

results = []

# ======================
# LOOP KEYWORDS
# ======================

for kw in keywords:

    print(f"\nProcessing: {kw}")

    payload = [{
        "keyword": kw,
        "location_name": "Italy",
        "language_code": "it",
        "depth": 10
    }]

    response = requests.post(
        "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        auth=HTTPBasicAuth(LOGIN, PASSWORD),
        json=payload
    )

    data = response.json()

    try:
        items = data["tasks"][0]["result"][0]["items"]

        for item in items:

            if item.get("type") != "organic":
                continue

            results.append({
                "keyword": kw,
                "position": item.get("rank_absolute"),
                "title": item.get("title"),
                "url": item.get("url"),
                "domain": item.get("domain"),
                "description": item.get("description")
            })

    except Exception as e:
        print("Errore:", e)
        print(json.dumps(data, indent=2))

# ======================
# EXPORT CSV
# ======================

if len(results) == 0:
    print("Nessun risultato trovato")
else:

    df = pd.DataFrame(results)

    df.to_csv("serp_results.csv", index=False)

    print("\n======================")
    print("FATTO")
    print("File salvato: serp_results.csv")
    print("======================")
