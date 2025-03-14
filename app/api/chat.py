from fastapi import APIRouter, HTTPException

from app.core.models.schema import ChatRequest, ChatResponse
from app.core.agents.intent_agent import IntentAgent
from app.core.agents.assistant_agent import AssistantAgent

from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        intent_topic_type = "IntentAgent"
        assistant_topic_type = "AssistantAgent"

        IntentAgent.add_subscription(intent_topic_type)
        AssistantAgent.add_subscription(assistant_topic_type)

        runtime = SingleThreadedAgentRuntime()

        await IntentAgent.register(
            runtime, type=intent_topic_type, factory=lambda: IntentAgent(model_client=model_client)
        )

        await AssistantAgent.register(runtime, type=assistant_topic_type, factory=lambda: AssistantAgent())

        runtime.start()

        result = await runtime.publish_message(
            UserMessage(content="An eco-friendly stainless steel water bottle that keeps drinks cold for 24 hours"),
            topic_id=TopicId(intent_topic_type, source="default"),
        )

        await runtime.stop_when_idle()


        return ChatResponse(answer=result[-1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))