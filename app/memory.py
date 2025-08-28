from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from models_db import User, ChatHistory
from fastapi import status
from database import SessionLocal, redis_client, REDIS_URL, REDIS_EXPIRATION_SECONDS
from typing import cast


def clear_guest_memory():
    session_key = f"message_store:{0}"
    redis_client.delete(session_key)


def load_memory(user_id: int) -> ConversationBufferMemory:
    session_key = f"message_store:{user_id}"
    # REDIS_URL is guaranteed to be str by database.py
    history = RedisChatMessageHistory(session_id=str(user_id), url=cast(str, REDIS_URL))

    redis_client.expire(session_key, REDIS_EXPIRATION_SECONDS)

    return ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, chat_memory=history
    )


def history_to_db(user_id, convo_id, user_message, ai_message, timestamp):
    session = SessionLocal()
    try:
        session.add_all(
            [
                ChatHistory(
                    user_id=user_id,
                    convo_id=convo_id,
                    message=user_message,
                    sender="user",
                    timestamp=timestamp,
                ),
                ChatHistory(
                    user_id=user_id,
                    convo_id=convo_id,
                    message=ai_message,
                    sender="assistant",
                    timestamp=timestamp,
                ),
            ]
        )
        session.commit()
        return {
            "message": "Chat history committed successfully",
            "status": status.HTTP_201_CREATED,
        }
    except Exception as e:
        session.rollback()
        return {
            "error": f"Failed to save chat history: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    finally:
        session.close()


def newUser_to_db(username, password, first_name, last_name, email, location):
    session = SessionLocal()
    try:
        new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            location=location,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user.id
    except Exception:
        session.rollback()
        return None
    finally:
        session.close()
