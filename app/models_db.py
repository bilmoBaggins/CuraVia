from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Enum, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.sql import func
from datetime import datetime
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
    closedChats: Mapped[list[int]] = mapped_column(JSON, default=list)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(
        default=False, nullable=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)


# ChatHistory table
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    convo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    sender: Mapped[SenderEnum] = mapped_column(Enum(SenderEnum))
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
