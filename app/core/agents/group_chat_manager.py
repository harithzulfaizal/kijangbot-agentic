import logging
from datetime import datetime
import re
from typing import Dict, List

from app.core.utils.chat_history import BufferedChatCompletionContext
from app.core.agents.runtime_orchestrator import BAgentType

from autogen_core import AgentId, MessageContext, RoutedAgent, default_subscription, message_handler
from autogen_core.model_context import Agent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from models.messages import (
    UserRequest,
    BAgentResponse
)



@default_subscription
class GroupChatManager(RoutedAgent):
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        session_id: str,
        user_id: str,
        memory: BufferedChatCompletionContext,
        agent_ids: Dict[BAgentType, AgentId],
    ):
        super().__init__("GroupChatManager")
        self._model_client = model_client
        self._session_id = session_id
        self._user_id = user_id
        self._memory = memory
        self._agent_ids = agent_ids  # Dictionary mapping AgentType to AgentId

    @message_handler
    async def handle_user_input(
        self, message: UserRequest, context: MessageContext
    ) -> BAgentResponse:
        """
        Handles the input task from the user. This is the initial message that starts the conversation.
        This method should create a new plan.
        """
        logging.info(f"Received input task: {message}")
        await self._memory.add_item(
            BAgentResponse(
                session_id=message.session_id,
                user_id=self._user_id,
                content=f"{message.description}",
                agent_id=self._agent_ids.get(BAgentType.human_agent),
                agent_name="HumanAgent"
            )
        )

        planner_agent_id = self._agent_ids.get(BAgentType.planner_agent)
        # plan: Plan = await self.send_message(message, planner_agent_id)
        logging.info(f"Plan created: {plan}")
        return plan

