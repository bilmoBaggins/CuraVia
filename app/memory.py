import os
import redis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models_db import ChatHistory
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set! Check your .env file.")

# Engine & session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Redis settings
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_EXPIRATION_SECONDS = int(os.getenv("REDIS_EXPIRATION_SECONDS", 24 * 3600))
redis_client = redis.Redis.from_url(REDIS_URL)


def load_memory(user_id: int) -> ConversationBufferMemory:
    session_key = f"message_store:{user_id}"
    history = RedisChatMessageHistory(session_id=str(user_id), url=REDIS_URL)

    redis_client.expire(session_key, REDIS_EXPIRATION_SECONDS)

    return ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, chat_memory=history
    )


def history_to_db(
    user_id: int, user_message: str, ai_message: str, timestamp: datetime
) -> None:
    session = SessionLocal()
    chats = [
        ChatHistory(
            user_id=user_id,
            message=user_message,
            sender="user",
            timestamp=timestamp,
        ),
        ChatHistory(
            user_id=user_id, message=ai_message, sender="ai", timestamp=timestamp
        ),
    ]
    session.add_all(chats)
    session.commit()
    session.close()
