from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class SenderEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    sender = Column(Enum(SenderEnum))
    timestamp = Column(TIMESTAMP, server_default=func.now())
