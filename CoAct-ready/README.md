#dodane
# CoAct (MVP) + Web RAG


## Co tu jest zrobione

1. **`rag_service/`** – mikroserwis FastAPI, który:
   - (opcjonalnie) robi web search,
   - pobiera strony z dokumentacją,
   - wyciąga treść (HTML → tekst),
   - chunki + embedding (Ollama `nomic-embed-text`),
   - zapis do **ChromaDB** (persist w volume),
   - zwraca **najbardziej relewantne fragmenty** + SOURCE URL.

2. **`src/tools/web_rag_tool.py`** – narzędzie (CrewAI Tool) `web_rag`, które wywołuje mikroserwis (`POST /ask`) i zwraca gotowy **context** do wklejenia w reasoning.

3. **Integracja w CrewAI** – wszyscy agenci dostają `tools=[WebRAGTool()]` i w promptach mają instrukcję: jeśli brakuje Ci aktualnej wiedzy o API/konfiguracji, użyj `web_rag`.

## Jak uruchomić

### 1) Odpal WebRAG + Ollama

```bash
docker compose up --build
```

- Ollama: `http://localhost:11434`
- WebRAG: `http://localhost:8001`

**Pierwsze odpalenie**: pobierz model embeddingu w Ollama (jeśli go nie masz):

```bash
ollama pull nomic-embed-text:latest
```

### 2) Odpal crew

W osobnym terminalu:

> Jeśli widzisz błąd `ModuleNotFoundError: No module named 'crewai'`, to znaczy, że nie masz zainstalowanych zależności.
> Najprościej: utwórz venv i zainstaluj requirements.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Następnie uruchom:

```bash
python -m src.main
```

## Konfiguracja (opcjonalnie)

- `RAG_SERVICE_URL` – gdzie działa WebRAG (domyślnie `http://localhost:8001`)
- `RAG_ALLOWED_DOMAINS` – allowlist domen (comma-separated), np.: `docs.python.org,fastapi.tiangolo.com`
- Search:
  - `TAVILY_API_KEY` albo `SERPER_API_KEY` (jeśli ustawisz, WebRAG użyje tych providerów)

## API mikroserwisu

- `GET /health`
- `POST /ingest` – indeksuje podane URL-e
- `POST /query` – pyta tylko wektorówkę (bez search)
- `POST /ask` – search + ingest + query w jednym kroku
