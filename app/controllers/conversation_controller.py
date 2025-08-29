from fastapi import status
from models_db import User, ChatHistory
from database import SessionLocal
from sqlalchemy import desc, func
from sqlalchemy.orm.attributes import flag_modified


async def get_conversations_logic(user_id):
    session = SessionLocal()
    try:
        convo_ids = (
            session.query(
                ChatHistory.convo_id, func.max(ChatHistory.timestamp).label("latest")
            )
            .filter(ChatHistory.user_id == user_id)
            .group_by(ChatHistory.convo_id)
            .order_by(desc("latest"))
            .all()
        )
        conversations = []
        for convo_id, _ in convo_ids:
            msgs = (
                session.query(ChatHistory)
                .filter(
                    ChatHistory.user_id == user_id, ChatHistory.convo_id == convo_id
                )
                .order_by(ChatHistory.timestamp)
                .all()
            )
            # Build a summary prompt from all user and assistant messages
            title = None
            if not title:
                if msgs:
                    title = msgs[0].message[:30]
                else:
                    max_convo = (
                        session.query(ChatHistory.convo_id)
                        .filter(ChatHistory.user_id == user_id)
                        .order_by(desc(ChatHistory.convo_id))
                        .first()
                    )
                    convo_id = (max_convo.convo_id + 1) if max_convo else 1
                    title = f"Chat {convo_id}"
            conversations.append({"id": convo_id, "title": title})
        return conversations
    finally:
        session.close()


async def create_conversation_logic(body):
    user_id = body.user_id
    session = SessionLocal()
    try:
        # Find max convo_id for user, increment
        max_convo = (
            session.query(ChatHistory.convo_id)
            .filter(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.convo_id))
            .first()
        )
        new_convo_id = (max_convo.convo_id + 1) if max_convo else 1

        return {
            "message": f"New conversation created with ID: {new_convo_id}",
            "status": status.HTTP_201_CREATED,
        }
    finally:
        session.close()


async def get_messages_logic(conversation_id, user_id):
    session = SessionLocal()
    try:
        messages = (
            session.query(ChatHistory)
            .filter(
                ChatHistory.convo_id == conversation_id, ChatHistory.user_id == user_id
            )
            .order_by(ChatHistory.timestamp)
            .all()
        )
        return [
            {"sender": m.sender, "text": m.message, "timestamp": m.timestamp}
            for m in messages
        ]
    finally:
        session.close()


async def get_closed_chats_logic(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.closedChats if user.closedChats else []
    finally:
        session.close()


async def add_closed_chat_logic(user_id, data):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found", "status": status.HTTP_404_NOT_FOUND}
        convo_id = data.get("convo_id")
        if convo_id is None:
            return {"error": "Missing convo_id", "status": status.HTTP_400_BAD_REQUEST}
        closed = user.closedChats if user.closedChats else []
        print(closed)
        if convo_id not in closed:
            closed.append(convo_id)
            print(closed)
            user.closedChats = closed
            flag_modified(user, "closedChats")
            session.commit()
        return {"closedChats": user.closedChats, "status": status.HTTP_200_OK}
    finally:
        session.close()
