
import os

from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

chat_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash-lite",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

reasoning_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash-thinking-exp-01-21",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)