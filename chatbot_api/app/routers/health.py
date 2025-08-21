from fastapi import APIRouter
from app.repositories.chroma_repo import collection

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready():
    cnt = collection().count()
    return {"status": "ready", "collection_count": str(cnt)}
