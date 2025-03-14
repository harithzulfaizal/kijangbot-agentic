# app/main.py
from fastapi import FastAPI
from app.api import chat, upload_file, delete_file # Import your API routers
from app.core.config import settings
import dotenv

dotenv.load_dotenv()

app = FastAPI(title="Agentic LLM Chatbot API", version="1.0.0")

app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)