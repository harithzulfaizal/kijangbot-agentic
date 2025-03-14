from fastapi import APIRouter, HTTPException
from app.core.agents.agent import Agent
from app.core.models.chat import ChatRequest, ChatResponse
from app.core.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService(Agent()) # Initialize your agent here.

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await chat_service.process_message(request.message, request.session_id)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))