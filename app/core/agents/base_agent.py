import logging
from typing import Any, List, Mapping

from utils.chat_history import BufferedCosmosDBChatHistory
from models.messages import UserRequest, BAgentResponse

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import (
    AssistantMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.tool_agent import tool_agent_caller_loop
from autogen_core.tools import Tool


class BaseAgent(RoutedAgent):
    def __init__(
        self,
        agent_name: str,
        model_client: OpenAIChatCompletionClient,
        session_id: str,
        user_id: str,
        model_context: BufferedCosmosDBChatHistory,
        tools: List[Tool],
        tool_agent_id: AgentId,
        system_message: str,
    ):
        super().__init__(agent_name)
        self._agent_name = agent_name
        self._model_client = model_client
        self._session_id = session_id
        self._user_id = user_id
        self._model_context = model_context
        self._tools = tools
        self._tool_schema = [tool.schema for tool in tools]
        self._tool_agent_id = tool_agent_id
        self._chat_history: List[LLMMessage] = [SystemMessage(system_message)]

    @message_handler
    async def handle_message(
        self, message: UserRequest, ctx: MessageContext
    ) -> BAgentResponse:
        
        try:
            messages: List[LLMMessage] = await tool_agent_caller_loop(
                caller=self,
                tool_agent_id=self._tool_agent_id,
                model_client=self._model_client,
                input_messages=self._chat_history,
                tool_schema=self._tools,
                cancellation_token=ctx.cancellation_token,
            )
            logging.info("*" * 12)
            logging.info(f"LLM call completed: {messages}")
            final_message = messages[-1]
            assert isinstance(final_message.content, str)
            result = final_message.content

            return BAgentResponse(
                session_id=message.session_id,
                user_id=self._user_id,
                message=result,
                agent_id=self._agent_id,
                agent_name=self._agent_name,
            )
            
        except Exception as e:
            print('Error')
