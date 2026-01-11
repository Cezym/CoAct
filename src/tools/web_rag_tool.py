"""CrewAI tool that queries the local WebRAG microservice.

The microservice (rag_service) is responsible for:
- web search (optional)
- downloading + extracting documentation pages
- indexing into Chroma
- retrieving relevant excerpts for the query

This tool returns a compact "context" string with SOURCE URLs + excerpts.
Agents can paste it into their reasoning and cite the sources.

Env vars
--------
RAG_SERVICE_URL: base url of the rag service (default: http://localhost:8001)
"""

from __future__ import annotations

import os

import requests
from pydantic import BaseModel, Field

try:
    # crewai_tools ships with CrewAI when installed with [tools]
    from crewai_tools import BaseTool
except Exception:  # pragma: no cover
    # Fallback type so the file can be imported even when tools extras aren't installed
    BaseTool = object  # type: ignore


class WebRAGInput(BaseModel):
    query: str = Field(..., description="Question to ask, e.g. 'How to configure FastAPI CORS middleware?' ")
    scope: str = Field(
        default="global",
        description="Namespace for cached docs. Use e.g. 'fastapi', 'react', 'numpy'.",
    )
    search: bool = Field(
        default=True,
        description="If true, service will do web search and ingest top results before querying.",
    )
    k: int = Field(default=6, ge=1, le=20, description="How many chunks to retrieve")
    max_search_results: int = Field(default=5, ge=1, le=10, description="How many web search results to consider")
    force_refresh: bool = Field(
        default=False,
        description="If true, re-download & re-index URLs even if already cached.",
    )

class WebRAGTool(BaseTool):
    name: str = "web_rag"
    description: str = (
        "Search and retrieve relevant documentation excerpts from the web (cached via local RAG). "
        "Use it when you need up-to-date API docs or examples for a library/tool. "
        "Returns SOURCE URLs + excerpts."
    )
    args_schema = WebRAGInput

    def _run(
            self,
            query: str,
            scope: str = "global",
            search: bool = True,
            k: int = 6,
            max_search_results: int = 5,
            force_refresh: bool = False,
    ) -> str:
        base = os.getenv("RAG_SERVICE_URL", "http://localhost:8001").rstrip("/")
        payload = {
            "query": query,
            "scope": scope,
            "search": search,
            "k": k,
            "max_search_results": max_search_results,
            "force_refresh": force_refresh,
        }
        try:
            resp = requests.post(f"{base}/ask", json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            return data.get("context", "") or ""
        except Exception as e:
            return (
                "[web_rag error] Could not reach WebRAG service. "
                f"Make sure docker-compose is running and RAG_SERVICE_URL is correct. Details: {e}"
            )
