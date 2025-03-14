from typing import List
from datetime import datetime
import pytz

pytz.timezone('Asia/Kuala_Lumpur')

from app.core.agents.base_agent import BaseAgent
from app.core.utils.chat_history import BufferedCosmosDBChatHistory
from app.core.models.llm import chat_client
from app.core.tools.web_search import get_relevant_web_pages

from autogen_core import AgentId, default_subscription
from autogen_core import default_subscription
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool, Tool

def get_assistant_tools() -> List[Tool]:
    AssistantTools: List[Tool] = [
        FunctionTool(
            get_relevant_web_pages,
            description="Create a new marketing campaign.",
            name="create_marketing_campaign",
        ),
    ]
    return AssistantTools


@default_subscription
class AssistantAgent(BaseAgent):
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        session_id: str,
        user_id: str,
        model_context: BufferedCosmosDBChatHistory,
        assistant_tools: List[Tool],
        assistant_tool_agent_id: AgentId
    ):
        super().__init__(
            "AssistantAgent",
            model_client,
            session_id,
            user_id,
            model_context,
            assistant_tools,
            assistant_tool_agent_id,
            (
                "You are, KijangBot, a helpful assistant.\n"
                f"Today's date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                "You have access to the following tools:\n"
                "1. get_relevant_web_pages\n"
                "   Useful for:\n"
                "       - User is asking about current events or something that requires real-time information (weather, sports scores, etc.)\n"
                "       - User is asking about some term you are totally unfamiliar with (it might be new)\n"
                "       - User explicitly asks you to browse or provide links to references\n"
            ),
        )