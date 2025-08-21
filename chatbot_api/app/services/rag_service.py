from typing import Any, Dict, List
from app.llm.openai_client import answer_with_context
from app.repositories import chroma_repo

def answer(query: str, k: int, metadata_fields: List[str] | None) -> tuple[str, List[Dict[str, Any]]]:
    docs, metas, ids = chroma_repo.retrieve(query, k)
    if not docs:
        return answer_with_context(query=query, context_blocks=[]), []
    sources: List[Dict[str, Any]] = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        src = {"id": ids[i] if i < len(ids) else None}
        if metadata_fields:
            src.update({k: (meta or {}).get(k) for k in metadata_fields})
        else:
            src.update(meta or {})
        src["preview"] = (doc[:240] + "...") if doc and len(doc) > 240 else (doc or "")
        sources.append(src)
    return answer_with_context(query=query, context_blocks=docs), sources
