"""
DataForSEO SERP Extractor
-------------------------
Estrae TUTTI i dati SERP estraibili da DataForSEO per una lista di keyword
e li salva in CSV + JSON.

Uso:
    1) Copia .env.example in .env e inserisci le tue credenziali DataForSEO
    2) Inserisci le keyword in keywords.csv (una per riga, colonna "keyword")
    3) python serp_extractor.py

Parametri principali modificabili da CLI:
    --location-code   (default 2380 = Italy)
    --language-code   (default "it")
    --device          (default "desktop", oppure "mobile")
    --depth           (default 100, numero risultati SERP)
    --input           (default "keywords.csv")
    --outdir          (default "output")
"""

import os
import json
import base64
import argparse
from datetime import datetime
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

LOGIN = os.getenv("DFS_LOGIN")
PASSWORD = os.getenv("DFS_PASSWORD")

# Endpoint "live/advanced" → ritorna TUTTI i blocchi SERP estraibili
ENDPOINT = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


# --------------------------------------------------------------------------- #
#                                 AUTH                                        #
# --------------------------------------------------------------------------- #
def auth_header():
    if not LOGIN or not PASSWORD:
        raise RuntimeError(
            "Credenziali DataForSEO mancanti. Imposta DFS_LOGIN e DFS_PASSWORD nel file .env"
        )
    token = base64.b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


# --------------------------------------------------------------------------- #
#                              API CALL                                       #
# --------------------------------------------------------------------------- #
def fetch_serp(keyword, location_code=2380, language_code="it",
               device="desktop", depth=100):
    """Chiamata SERP live/advanced per una singola keyword."""
    payload = [{
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": device,
        "depth": depth,
        "calculate_rectangles": True,
        "people_also_ask_click_depth": 4,
    }]
    r = requests.post(ENDPOINT, headers=auth_header(),
                      data=json.dumps(payload), timeout=90)
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------------- #
#                              PARSING                                        #
# --------------------------------------------------------------------------- #
def parse_items(keyword, response):
    """
    Trasforma la risposta in righe tabellari.
    Tiene TUTTI i tipi di item: organic, paid, featured_snippet, people_also_ask,
    video, images, local_pack, knowledge_graph, related_searches, top_stories,
    twitter, shopping, ecc.
    """
    rows = []
    tasks = response.get("tasks") or []
    for task in tasks:
        results = task.get("result") or []
        for result in results:
            se_results_count = result.get("se_results_count")
            spell = result.get("spell")
            items = result.get("items") or []
            for item in items:
                rows.append({
                    "keyword": keyword,
                    "se_results_count": se_results_count,
                    "spell_correction": (spell or {}).get("keyword"),
                    "type": item.get("type"),
                    "rank_group": item.get("rank_group"),
                    "rank_absolute": item.get("rank_absolute"),
                    "position": item.get("position"),
                    "title": item.get("title"),
                    "domain": item.get("domain"),
                    "url": item.get("url"),
                    "breadcrumb": item.get("breadcrumb"),
                    "description": item.get("description"),
                    "is_featured_snippet": item.get("is_featured_snippet"),
                    "is_malicious": item.get("is_malicious"),
                    "is_web_story": item.get("is_web_story"),
                    "amp_version": item.get("amp_version"),
                    "rating_value": (item.get("rating") or {}).get("value"),
                    "rating_votes": (item.get("rating") or {}).get("votes_count"),
                    "price_current": (item.get("price") or {}).get("current"),
                    "price_currency": (item.get("price") or {}).get("currency"),
                    "highlighted": ", ".join(item.get("highlighted") or []) if item.get("highlighted") else None,
                    "links_count": len(item.get("links") or []),
                    "extra": json.dumps(item.get("extra"), ensure_ascii=False) if item.get("extra") else None,
                    "about_this_result": json.dumps(item.get("about_this_result"), ensure_ascii=False)
                        if item.get("about_this_result") else None,
                    # campi specifici di alcuni blocchi:
                    "items_inner": json.dumps(item.get("items"), ensure_ascii=False)
                        if item.get("items") else None,
                })
    return rows


def parse_serp_overview(keyword, response):
    """Riepilogo per keyword (1 riga per kw)."""
    tasks = response.get("tasks") or []
    if not tasks:
        return {"keyword": keyword, "status": "no_task"}
    task = tasks[0]
    result = (task.get("result") or [{}])[0]
    items = result.get("items") or []
    types_count = {}
    for it in items:
        t = it.get("type", "unknown")
        types_count[t] = types_count.get(t, 0) + 1
    return {
        "keyword": keyword,
        "status_code": task.get("status_code"),
        "status_message": task.get("status_message"),
        "se_results_count": result.get("se_results_count"),
        "items_count": result.get("items_count"),
        "check_url": result.get("check_url"),
        "datetime": result.get("datetime"),
        "spell_correction": (result.get("spell") or {}).get("keyword"),
        "types_breakdown": json.dumps(types_count, ensure_ascii=False),
    }


# --------------------------------------------------------------------------- #
#                                MAIN                                         #
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="DataForSEO SERP Extractor")
    parser.add_argument("--input", default="keywords.csv",
                        help="CSV con colonna 'keyword'")
    parser.add_argument("--outdir", default="output", help="Cartella output")
    parser.add_argument("--location-code", type=int, default=2380,
                        help="Codice location DataForSEO (2380=Italy, 2840=USA)")
    parser.add_argument("--language-code", default="it",
                        help="Codice lingua (it, en, es, fr, de, ...)")
    parser.add_argument("--device", default="desktop",
                        choices=["desktop", "mobile"])
    parser.add_argument("--depth", type=int, default=100,
                        help="Numero di risultati SERP (max 700)")
    args = parser.parse_args()

    # Carica keyword
    df_kw = pd.read_csv(args.input)
    if "keyword" not in df_kw.columns:
        raise ValueError("Il CSV di input deve contenere una colonna 'keyword'.")
    keywords = df_kw["keyword"].dropna().astype(str).str.strip().unique().tolist()
    print(f"📋 {len(keywords)} keyword da processare\n")

    # Crea output dir
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_rows = []
    overview_rows = []
    raw_dump = {}

    for kw in tqdm(keywords, desc="Estrazione SERP"):
        try:
            resp = fetch_serp(
                keyword=kw,
                location_code=args.location_code,
                language_code=args.language_code,
                device=args.device,
                depth=args.depth,
            )
            raw_dump[kw] = resp
            all_rows.extend(parse_items(kw, resp))
            overview_rows.append(parse_serp_overview(kw, resp))
        except Exception as e:
            print(f"❌ Errore su '{kw}': {e}")
            overview_rows.append({"keyword": kw, "status": f"error: {e}"})

    # Salva CSV dettagliato
    df_items = pd.DataFrame(all_rows)
    items_csv = outdir / f"serp_items_{ts}.csv"
    df_items.to_csv(items_csv, index=False, encoding="utf-8-sig")

    # Salva overview
    df_overview = pd.DataFrame(overview_rows)
    overview_csv = outdir / f"serp_overview_{ts}.csv"
    df_overview.to_csv(overview_csv, index=False, encoding="utf-8-sig")

    # Salva JSON grezzo (per analisi avanzate)
    raw_json = outdir / f"serp_raw_{ts}.json"
    with open(raw_json, "w", encoding="utf-8") as f:
        json.dump(raw_dump, f, ensure_ascii=False, indent=2)

    print("\n✅ Estrazione completata!")
    print(f"   • Dettaglio item : {items_csv}  ({len(df_items)} righe)")
    print(f"   • Riepilogo kw   : {overview_csv}")
    print(f"   • JSON raw       : {raw_json}")


if __name__ == "__main__":
    main()
