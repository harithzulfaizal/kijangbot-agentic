
import uuid
from typing import List, Optional, Tuple, Dict
from enum import Enum

from app.core.utils.chat_history import BufferedCosmosDBChatHistory
from app.core.models.llm import chat_client
from app.core.agents.intent_agent import IntentAgent
from app.core.agents.assistant_agent import AssistantAgent, get_assistant_tools

from autogen_core import SingleThreadedAgentRuntime, AgentId
from autogen_core.tool_agent import ToolAgent
from autogen_core.tools import Tool

class BAgentType(str, Enum):
    """Enumeration of agent types."""

    human_agent = "HumanAgent"
    assistant_agent = "AssistantAgent"
    intent_agent = "IntentAgent"
    group_chat_manager = "GroupChatManager"
    planner_agent = "PlannerAgent"


runtime_dict: Dict[
    str, Tuple[SingleThreadedAgentRuntime, BufferedCosmosDBChatHistory]
] = {}

model_client = chat_client

assistant_tools = get_assistant_tools()

async def initialize_runtime_and_context(
    session_id: Optional[str] = None, user_id: str = None
) -> Tuple[SingleThreadedAgentRuntime, BufferedCosmosDBChatHistory]:
    """
    Initializes agents and context for a given session.

    Args:
        session_id (Optional[str]): The session ID.

    Returns:
        Tuple[SingleThreadedAgentRuntime, CosmosBufferedChatCompletionContext]: The runtime and context for the session.
    """
    global runtime_dict
    global model_client

    if user_id is None:
        raise ValueError(
            "The 'user_id' parameter cannot be None. Please provide a valid user ID."
        )

    if session_id is None:
        session_id = str(uuid.uuid4())

    if session_id in runtime_dict:
        return runtime_dict[session_id]

    # Initialize agents with AgentIds that include session_id to ensure uniqueness
    intent_agent_id = AgentId("intent_agent", session_id)
    assistant_agent_id = AgentId("assistant_agent", session_id)
    assistant_tool_agent_id = AgentId("assistant_tool_agent", session_id)

    group_chat_manager_id = AgentId("group_chat_manager", session_id)

    # Initialize the context for the session
    cosmos_memory = BufferedCosmosDBChatHistory(session_id, user_id)

    # Initialize the runtime for the session
    runtime = SingleThreadedAgentRuntime(tracer_provider=None)

    # Register tool agents
    await ToolAgent.register(
        runtime, "assistant_tool_agent",
        lambda: ToolAgent("Assistant tool execution agent", assistant_tools)
    )

    # Register agents with unique AgentIds per session
    await IntentAgent.register(
        runtime,
        intent_agent_id.type,
        lambda: IntentAgent(
            model_client,
            session_id,
            user_id,
            cosmos_memory,
            assistant_agent_id,
            [
                agent.type
                for agent in [
                    assistant_agent_id
                ]
            
            ]
        ),
    )
    await AssistantAgent.register(
        runtime,
        assistant_agent_id.type,
        lambda: AssistantAgent(
            model_client,
            session_id,
            user_id,
            cosmos_memory,
            assistant_tool_agent_id,
        ),
    )

    # await HumanAgent.register(
    #     runtime,
    #     human_agent_id.type,
    #     lambda: HumanAgent(cosmos_memory, user_id, group_chat_manager_id),
    # )

    agent_ids = {
        BAgentType.intent_agent: intent_agent_id,
        BAgentType.assistant_agent: assistant_agent_id,
        # BAgentType.human_agent: human_agent_id,
    }

    await GroupChatManager.register(
        runtime,
        group_chat_manager_id.type,
        lambda: GroupChatManager(
            model_client=model_client,
            session_id=session_id,
            user_id=user_id,
            memory=cosmos_memory,
            agent_ids=agent_ids,
        ),
    )

    runtime.start()
    runtime_dict[session_id] = (runtime, cosmos_memory)
    return runtime_dict[session_id]

def retrieve_all_agent_tools() -> List[Dict[str, Any]]:
    assistant_tools: List[Tool] = get_assistant_tools()

    functions = []

    for tool in assistant_tools:
        functions.append(   
            {
                "agent": "IntentAgent",
                "function": tool.name,
                "description": tool.description,
                "arguments": str(tool.schema["parameters"]["properties"])
            }
        )

    return functions