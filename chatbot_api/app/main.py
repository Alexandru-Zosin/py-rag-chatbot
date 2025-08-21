from fastapi import FastAPI
from app.routers import health, chat

app = FastAPI(title="chatbot_api", version="0.2.0")
app.include_router(health.router)
app.include_router(chat.router)
