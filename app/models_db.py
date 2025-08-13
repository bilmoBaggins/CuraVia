from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
import enum

# Base class
class Base(DeclarativeBase):
    pass

# Enum for sender
class SenderEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"

# User table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped = mapped_column(TIMESTAMP, server_default=func.now())

# ChatHistory table
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    sender: Mapped[SenderEnum] = mapped_column(Enum(SenderEnum))
    timestamp: Mapped = mapped_column(TIMESTAMP, server_default=func.now())
