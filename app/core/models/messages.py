from typing import List, Dict, Optional
from pydantic import BaseModel

class UserRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class BAgentResponse(BaseModel):
    session_id: str
    user_id: str
    message: str
    agent_id: str
    agent_name: str