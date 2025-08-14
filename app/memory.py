import os
import redis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from database import get_mysql_connection

# Redis settings
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_EXPIRATION_SECONDS = int(os.getenv("REDIS_EXPIRATION_SECONDS", 24 * 3600))
redis_client = redis.Redis.from_url(REDIS_URL)


class CustomMemory(ConversationBufferMemory):
    def add_user_message(self, message: str):
        super().add_user_message(message)  # type: ignore
        save_message_to_db(
            sender="user",
            message=message,
            timestamp=self.chat_memory.get_last_message_timestamp(),  # type: ignore
        )

    def add_ai_message(self, message: str):
        super().add_ai_message(message)  # type: ignore
        save_message_to_db(
            sender="ai",
            message=message,
            timestamp=self.chat_memory.get_last_message_timestamp(),  # type: ignore
        )


def load_memory(user_id: int) -> CustomMemory:
    """
    Load conversation memory for a given user.
    Stores history in Redis and also persists each message to MySQL.
    """
    # session_key = f"message_store:{user_id}"
    history = RedisChatMessageHistory(
        session_id=str(user_id), url=REDIS_URL
    )  # type: ignore

    return CustomMemory(
        memory_key="chat_history", return_messages=True, chat_memory=history
    )


def save_message_to_db(message: str, sender: str, timestamp: str):
    """
    Append a single message to the MySQL chat_history table.
    """
    conn = get_mysql_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history (message, sender, timestamp)
            VALUES (%s, %s, %s)
            """,
            (message, sender, timestamp),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
