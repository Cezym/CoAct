

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Optional deps (kept optional to avoid hard crashes if you only use /ingest with explicit URLs)
try:
    import trafilatura  # type: ignore
except Exception:  # pragma: no cover
    trafilatura = None

try:
    from ddgs import DDGS  # type: ignore
except Exception:  # pragma: no cover
    DDGS = None

try:
    import chromadb  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependency 'chromadb'. Install requirements.txt in rag_service."
    ) from e


# -----------------------------
# Settings
# -----------------------------

@dataclass(frozen=True)
class Settings:
    data_dir: str = os.getenv("RAG_DATA_DIR", "/data")
    chroma_dir: str = os.getenv("CHROMA_DIR", "/data/chroma")

    ollama_url: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")

    # Search provider keys (optional)
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    serper_api_key: str | None = os.getenv("SERPER_API_KEY")

    # Safety/ops
    http_timeout_s: float = float(os.getenv("RAG_HTTP_TIMEOUT_S", "20"))
    max_download_bytes: int = int(os.getenv("RAG_MAX_DOWNLOAD_BYTES", str(2_000_000)))
    user_agent: str = os.getenv(
        "RAG_USER_AGENT",
        "CoActWebRAG/0.1 (+https://example.local; contact=dev@local)",
    )

    # Allowlist domains (comma-separated). If empty -> allow all.
    # NOTE: dataclasses forbids mutable defaults, so we must use default_factory.
    allowed_domains: List[str] = field(
        default_factory=lambda: [
            d.strip().lower()
            for d in os.getenv("RAG_ALLOWED_DOMAINS", "").split(",")
            if d.strip()
        ]
    )


SETTINGS = Settings()


# -----------------------------
# Helpers
# -----------------------------

def _safe_collection_name(scope: str) -> str:
    scope = scope.strip().lower() or "global"
    scope = re.sub(r"[^a-z0-9_\-]", "_", scope)
    return f"webdocs_{scope}"[:63]


def _hash_id(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h


def _domain(url: str) -> str:
    m = re.match(r"https?://([^/]+)/?", url.strip(), re.I)
    return (m.group(1).lower() if m else "")


def _domain_allowed(url: str) -> bool:
    if not SETTINGS.allowed_domains:
        return True
    d = _domain(url)
    return any(d == allow or d.endswith("." + allow) for allow in SETTINGS.allowed_domains)


def fetch_url(url: str) -> str:
    if not _domain_allowed(url):
        raise HTTPException(status_code=400, detail=f"Domain not allowed: {url}")

    headers = {"User-Agent": SETTINGS.user_agent}
    with requests.get(url, headers=headers, timeout=SETTINGS.http_timeout_s, stream=True) as r:
        r.raise_for_status()
        content = b""
        for chunk in r.iter_content(chunk_size=32_768):
            if not chunk:
                continue
            content += chunk
            if len(content) > SETTINGS.max_download_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"Downloaded content too large (> {SETTINGS.max_download_bytes} bytes): {url}",
                )

    # Try to decode with apparent encoding fallback
    enc = r.encoding or "utf-8"
    try:
        return content.decode(enc, errors="replace")
    except Exception:
        return content.decode("utf-8", errors="replace")


def extract_main_text(html: str, url: str) -> str:
    # Best effort extraction
    if trafilatura is not None:
        try:
            downloaded = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                favor_recall=True,
            )
            if downloaded:
                return downloaded
        except Exception:
            pass

    # Fallback: strip tags very roughly
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_chars: int = 1600, overlap: int = 200) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


# -----------------------------
# Search
# -----------------------------

def search_web(query: str, max_results: int = 5) -> List[str]:
    query = query.strip()
    if not query:
        return []

    # 1) Tavily
    if SETTINGS.tavily_api_key:
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": SETTINGS.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                },
                timeout=SETTINGS.http_timeout_s,
            )
            resp.raise_for_status()
            data = resp.json()
            urls = [r.get("url") for r in data.get("results", []) if r.get("url")]
            return urls[:max_results]
        except Exception:
            pass

    # 2) Serper (Google)
    if SETTINGS.serper_api_key:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SETTINGS.serper_api_key},
                json={"q": query, "num": max_results},
                timeout=SETTINGS.http_timeout_s,
            )
            resp.raise_for_status()
            data = resp.json()
            urls = [r.get("link") for r in data.get("organic", []) if r.get("link")]
            return urls[:max_results]
        except Exception:
            pass

    # 3) DuckDuckGo fallback
    if DDGS is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "No search provider configured. Set TAVILY_API_KEY or SERPER_API_KEY, "
                "or install duckduckgo_search in the rag_service container."
            ),
        )

    urls: List[str] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                u = r.get("href") or r.get("url")
                if u:
                    urls.append(u)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Search failed: {e}")

    # Basic de-dup
    out: List[str] = []
    seen = set()
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out[:max_results]


# -----------------------------
# Embeddings + Vector store
# -----------------------------
class OllamaEmbeddingFunction:
    """Embedding function compatible with Chroma + Ollama (/api/embed)."""

    def __init__(self, base_url: str, model: str, timeout_s: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_s = timeout_s
        self.is_legacy = False  # some Chroma versions check this

    def name(self) -> str:
        return "ollama"

    def get_config(self) -> dict:
        return {"base_url": self.base_url, "model": self.model}

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        try:
            # Use the modern Ollama embeddings endpoint
            resp = requests.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
                timeout=self.timeout_s,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            # Fallback debug info
            print(f"Ollama embedding error: {e}")
            raise RuntimeError(f"Ollama connection failed: {e}")

        # Handle various Ollama response formats
        embs = data.get("embeddings")
        
        # Fallback for older Ollama or different response structure
        if not embs and "embedding" in data:
            embs = [data["embedding"]]

        if not embs:
            # Empty response
            return []

        # CRITICAL FIX: Normalize shape.
        # We need List[List[float]].
        # If Ollama returns a flat list [0.1, 0.2, ...], wrap it.
        first_item = embs[0]
        
        # Case 1: It's a flat list of floats (single vector returned incorrectly)
        if isinstance(first_item, (int, float)):
            return [embs]
            
        # Case 2: It's a list of lists (Correct)
        if isinstance(first_item, list):
            return embs

        raise RuntimeError(f"Invalid embeddings shape from Ollama: {type(first_item)}")

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        # Chroma passes a list[str]
        return self._embed_texts(list(input))

    def embed_query(self, input) -> List[List[float]]:
        # Chroma rust oczekuje query_embeddings jako List[List[float]]
        if isinstance(input, list):
            texts = [str(x) for x in input]
        else:
            texts = [str(input)]
        return self._embed_texts(texts)


    def __call__(self, input) -> List[List[float]]:
        # Chroma EmbeddingFunction interface backwards compatibility
        if isinstance(input, str):
            texts = [input]
        else:
            texts = list(input)
        return self._embed_texts(texts)



_embedder = OllamaEmbeddingFunction(
    base_url=SETTINGS.ollama_url,
    model=SETTINGS.embed_model,
    timeout_s=SETTINGS.http_timeout_s,
)


def _chroma_client() -> Any:
    os.makedirs(SETTINGS.chroma_dir, exist_ok=True)
    return chromadb.PersistentClient(path=SETTINGS.chroma_dir)


def get_collection(scope: str):
    client = _chroma_client()
    name = _safe_collection_name(scope)
    return client.get_or_create_collection(name=name, embedding_function=_embedder)


def already_ingested(collection, url: str) -> bool:
    # Chroma filtering support depends on version; we try a cheap heuristic:
    try:
        res = collection.get(where={"url": url}, limit=1)
        ids = res.get("ids") if isinstance(res, dict) else None
        return bool(ids)
    except Exception:
        return False


def upsert_url(collection, url: str, text: str, chunk_chars: int, overlap: int) -> int:
    chunks = chunk_text(text, chunk_chars=chunk_chars, overlap=overlap)
    if not chunks:
        return 0

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    ts = int(time.time())
    for i, ch in enumerate(chunks):
        ids.append(_hash_id(url, str(i)))
        docs.append(ch)
        metas.append({"url": url, "chunk": i, "ingested_at": ts})

    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(chunks)


def retrieve(collection, query: str, k: int = 6) -> List[Tuple[str, str, float]]:
    # Returns list of (url, chunk_text, distance)
    res = collection.query(query_texts=[query], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    out: List[Tuple[str, str, float]] = []
    for doc, meta, dist in zip(docs, metas, dists):
        url = meta.get("url") if isinstance(meta, dict) else ""
        out.append((url or "", doc or "", float(dist)))
    return out


def format_context(items: List[Tuple[str, str, float]], max_chars: int = 6000) -> str:
    # Smaller distance typically means more relevant for Chroma; we don't over-interpret.
    parts: List[str] = []
    total = 0
    used_urls: List[str] = []

    for url, text, dist in items:
        snippet = text.strip()
        if not snippet:
            continue

        block = (
            f"SOURCE: {url}\n"
            f"RELEVANCE_DISTANCE: {dist:.4f}\n"
            f"CONTENT:\n{snippet}\n"
            f"---\n"
        )
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
        if url and url not in used_urls:
            used_urls.append(url)

    header = (
        "You can use the following retrieved documentation excerpts. "
        "Cite the SOURCE URLs when referencing details.\n\n"
    )
    return header + "".join(parts)


# -----------------------------
# API models
# -----------------------------

class IngestRequest(BaseModel):
    urls: List[str] = Field(default_factory=list)
    scope: str = "global"
    force_refresh: bool = False
    chunk_chars: int = 1600
    overlap: int = 200


class IngestResponse(BaseModel):
    scope: str
    ingested_urls: int
    ingested_chunks: int
    skipped_urls: int
    errors: List[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    query: str
    scope: str = "global"
    k: int = 6


class QueryResponse(BaseModel):
    scope: str
    context: str
    sources: List[str]


class AskRequest(BaseModel):
    query: str
    scope: str = "global"
    search: bool = True
    max_search_results: int = 5
    max_urls_to_ingest: int = 5
    force_refresh: bool = False
    k: int = 6


class AskResponse(BaseModel):
    scope: str
    context: str
    sources: List[str]
    ingested_urls: int
    ingested_chunks: int


# -----------------------------
# FastAPI
# -----------------------------

app = FastAPI(title="CoAct WebRAG", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    if not req.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    collection = get_collection(req.scope)

    ingested_urls = 0
    ingested_chunks = 0
    skipped = 0
    errors: List[str] = []

    for url in req.urls[:50]:  # hard cap
        try:
            if (not req.force_refresh) and already_ingested(collection, url):
                skipped += 1
                continue

            html = fetch_url(url)
            text = extract_main_text(html, url=url)
            if len(text) < 200:
                errors.append(f"Too little extracted text: {url}")
                continue

            chunks = upsert_url(
                collection,
                url=url,
                text=text,
                chunk_chars=req.chunk_chars,
                overlap=req.overlap,
            )
            if chunks:
                ingested_urls += 1
                ingested_chunks += chunks
        except Exception as e:
            errors.append(f"{url}: {e}")

    return IngestResponse(
        scope=req.scope,
        ingested_urls=ingested_urls,
        ingested_chunks=ingested_chunks,
        skipped_urls=skipped,
        errors=errors,
    )


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    collection = get_collection(req.scope)
    items = retrieve(collection, req.query, k=max(1, min(req.k, 20)))
    context = format_context(items)
    sources = [u for (u, _, _) in items if u]
    # de-dup preserve order
    seen = set()
    sources = [u for u in sources if not (u in seen or seen.add(u))]

    return QueryResponse(scope=req.scope, context=context, sources=sources)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    query_txt = req.query.strip()
    if not query_txt:
        raise HTTPException(status_code=400, detail="Empty query")

    urls: List[str] = []
    if req.search:
        urls = search_web(query_txt, max_results=max(1, min(req.max_search_results, 10)))

    # Simple heuristic: docs-first preference
    def score_url(u: str) -> int:
        u2 = u.lower()
        score = 0
        for kw in ["docs", "documentation", "api", "reference", "readthedocs", "github.com"]:
            if kw in u2:
                score += 1
        return score

    urls = sorted(urls, key=score_url, reverse=True)[: max(0, min(req.max_urls_to_ingest, 10))]

    ingested_urls = 0
    ingested_chunks = 0
    if urls:
        ir = ingest(
            IngestRequest(
                urls=urls,
                scope=req.scope,
                force_refresh=req.force_refresh,
            )
        )
        ingested_urls = ir.ingested_urls
        ingested_chunks = ir.ingested_chunks

    qr = query(QueryRequest(query=query_txt, scope=req.scope, k=req.k))
    return AskResponse(
        scope=req.scope,
        context=qr.context,
        sources=qr.sources,
        ingested_urls=ingested_urls,
        ingested_chunks=ingested_chunks,
    )