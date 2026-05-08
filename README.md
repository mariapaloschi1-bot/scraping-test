# 🔎 DataForSEO SERP Extractor

Mini-tool Python che, data una lista di keyword, estrae **tutti i dati SERP estraibili** da DataForSEO (Google Organic - endpoint `live/advanced`) e li salva in CSV + JSON.

Vengono catturati tutti i blocchi SERP: **organic**, **paid**, **featured snippet**, **people also ask**, **video**, **images**, **local pack**, **knowledge graph**, **related searches**, **top stories**, **shopping**, ecc.

---

## 🚀 Setup

```bash
# 1. Clona la repo
git clone https://github.com/TUO-USERNAME/dataforseo-serp-tool.git
cd dataforseo-serp-tool

# 2. (consigliato) crea un virtualenv
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Configura le credenziali
cp .env.example .env
# poi apri .env e inserisci DFS_LOGIN e DFS_PASSWORD
# (le trovi su https://app.dataforseo.com/api-access)
```

---

## 🗒️ Inserisci le keyword

Apri `keywords.csv` e inserisci una keyword per riga (colonna `keyword`):

```csv
keyword
scarpe running uomo
migliori cuffie bluetooth
ricetta pasta carbonara
```

---

## ▶️ Esecuzione

Comando base:

```bash
python serp_extractor.py
```

Con parametri personalizzati:

```bash
python serp_extractor.py \
  --input keywords.csv \
  --outdir output \
  --location-code 2380 \
  --language-code it \
  --device desktop \
  --depth 100
```

| Parametro          | Default        | Descrizione |
|--------------------|----------------|-------------|
| `--input`          | `keywords.csv` | CSV con colonna `keyword` |
| `--outdir`         | `output`       | Cartella di output |
| `--location-code`  | `2380` (Italy) | Codice location DataForSEO (2840=USA, 2826=UK, ecc.) |
| `--language-code`  | `it`           | Codice lingua |
| `--device`         | `desktop`      | `desktop` o `mobile` |
| `--depth`          | `100`          | Numero risultati SERP (max 700) |

---

## 📦 Output

Nella cartella `output/` vengono salvati 3 file con timestamp:

- **`serp_items_YYYYMMDD_HHMMSS.csv`** — riga per ogni item SERP (tipo, posizione, URL, titolo, descrizione, rating, prezzo, ecc.)
- **`serp_overview_YYYYMMDD_HHMMSS.csv`** — 1 riga per keyword con riepilogo (numero risultati, breakdown per tipo di blocco, status)
- **`serp_raw_YYYYMMDD_HHMMSS.json`** — risposta JSON grezza completa (utile per estrazioni custom)

---

## 💡 Codici location utili

| Paese    | Codice |
|----------|--------|
| Italia   | 2380   |
| USA      | 2840   |
| UK       | 2826   |
| Spagna   | 2724   |
| Francia  | 2250   |
| Germania | 2276   |

Lista completa: <https://docs.dataforseo.com/v3/serp/google/locations/>

---

## ⚠️ Note

- L'endpoint `live/advanced` consuma crediti DataForSEO ad ogni keyword. Controlla i prezzi su [dataforseo.com/pricing](https://dataforseo.com/pricing).
- Il file `.env` è nel `.gitignore`: **non committare mai le credenziali**.
- Per grandi liste di keyword (>500) considera l'endpoint `task_post` + `task_get` (più economico in batch).

---

## 📄 Licenza

MIT
