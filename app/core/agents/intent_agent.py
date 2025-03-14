from typing import List

from agents.base_agent import BaseAgent
from utils.chat_history import BufferedCosmosDBChatHistory
from models.llm import chat_client

from autogen_core import AgentId, default_subscription
from autogen_core import default_subscription
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool, Tool

@default_subscription
class IntentAgent(BaseAgent):
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        session_id: str,
        user_id: str,
        model_context: BufferedCosmosDBChatHistory,
    ):
        super().__init__(
            "IntentAgent",
            model_client,
            session_id,
            user_id,
            model_context,
            (
                "You are an AI Agent specialized in detecting intent based on the user's input.\n"
                "Based on the input from the user, you must decide the which large language model to be used to answer the query.\n"
                "You have access to two models:\n"
                "   1. chat: is used for general query, simple information retrieval and simple mathematics\n"
                "   2. reasoning: is used for complex task requiring analytical reasoning capabilities especially in STEM related queries, coding and debugging, planning\n"
                "If the query explicitly states to use a chat mode, you must always use chat.\n"
                "If the query explicitly states to use a reasoning mode, you must always use reasoning.\n"
                "If the query is vague, always default to chat.\n"

            ),
        )