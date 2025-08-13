import os
import redis
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_EXPIRATION_SECONDS = int(os.getenv("REDIS_EXPIRATION_SECONDS", 1 * 24 * 3600))

redis_client = redis.Redis.from_url(REDIS_URL)


def load_memory(user_id: int) -> ConversationBufferMemory:
    session_key = f"message_store:{user_id}"
    # Convert session_id to str
    history = RedisChatMessageHistory(session_id=str(user_id), url=REDIS_URL)

    # Rolling TTL: refresh expiration on every access
    redis_client.expire(session_key, REDIS_EXPIRATION_SECONDS)

    return ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, chat_memory=history
    )
