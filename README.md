# DataForSEO SERP Scraper

Scarica la top 10 Google per una lista di keyword usando DataForSEO.

## Installazione

### 1. Crea virtual env

```bash
python -m venv venv
```

### 2. Attiva virtual env

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura .env

```env
DATAFORSEO_LOGIN=tua_email
DATAFORSEO_PASSWORD=tua_password_api
```

### 5. Inserisci keyword

Modifica:

```text
keywords.txt
```

### 6. Avvia script

```bash
python main.py
```

## Output

Viene creato:

```text
serp_results.csv
```
