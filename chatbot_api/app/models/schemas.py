from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    k: int = 4
    metadata_fields: Optional[List[str]] = None

class Source(BaseModel):
    id: Optional[str] = None
    preview: str = ""
    extra: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
