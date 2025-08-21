from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services import rag_service
from app.services import summary_tool

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    q = req.query.strip()
    lower = q.lower()
    summary_intent = (
        "summary" in lower or lower.startswith("summarize ") or lower.startswith("summary:")
    )
    if summary_intent:
        answer = summary_tool.run(q)
        return ChatResponse(answer=answer, sources=[])
    answer, sources = rag_service.answer(q, req.k, req.metadata_fields)
    return ChatResponse(answer=answer, sources=sources)
