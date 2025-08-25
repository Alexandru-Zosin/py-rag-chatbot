from typing import Any, Dict, List, Tuple
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from app.core.config import settings

_client = None
_collection = None

def _embedding_fn() -> OpenAIEmbeddingFunction:
    return OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=settings.openai_embedding_model,
    )

def collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    _client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    _collection = _client.get_or_create_collection(
        name=settings.chroma_collection,
        embedding_function=_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )
    return _collection

class SummaryNotFound(Exception):
    pass

def retrieve(query: str, k: int) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
    res = collection().query(query_texts=[query], n_results=k)
    docs = res.get("documents", [[]])[0] if res.get("documents") else []
    metas = res.get("metadatas", [[]])[0] if res.get("metadatas") else []
    ids = res.get("ids", [[]])[0] if res.get("ids") else []
    return docs, metas, ids

def get_summary_for_title(title: str) -> str:
    try:
        exact = collection().get(where={"title": {"$eq": title}})
        if exact and exact.get("ids"):
            meta = (exact.get("metadatas") or [{}])[0] or {}
            doc = (exact.get("documents") or [""])[0] or ""
            summary = meta.get("summary")
            return summary if summary else _compact(doc)
    except Exception:
        pass

    q = collection().query(query_texts=[title], n_results=1)
    docs = q.get("documents", [[]])[0] if q.get("documents") else []
    metas = q.get("metadatas", [[]])[0] if q.get("metadatas") else []
    if not docs:
        raise SummaryNotFound(f"No item found for title='{title}'")
    summary = (metas[0] or {}).get("summary") if metas else None
    return summary if summary else _compact(docs[0])

def _compact(text: str, max_chars: int = 800) -> str:
    t = (text or "").strip().replace("\n", " ")
    return t if len(t) <= max_chars else t[: max_chars - 3] + "..."
