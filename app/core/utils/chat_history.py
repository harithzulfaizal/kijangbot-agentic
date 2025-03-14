import os
from typing import List, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.core.config import Config

from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import LLMMessage


class BufferedCosmosDBChatHistory(BufferedChatCompletionContext):
    def __init__(
            self,
            session_id: str,
            user_id: str,
            buffer_size: int = 20,
            initial_messages: Optional[List[LLMMessage]] = None,
    ) -> None:
        super().__init__(buffer_size=buffer_size, initial_messages=initial_messages)

        self._cosmosdb_client = Config.get_cosmosdb_client()
        self._session_id = session_id
        self._user_id = user_id
        self._client = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))

    