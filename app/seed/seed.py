import os
import enum
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Integer,
    String,
    Text,
    Enum,
    ForeignKey,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set! Check your .env file.")

# Engine & session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


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


# BackgroundJobs table
class BackgroundJobs(Base):
    __tablename__ = "background_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Seeder function
def seed() -> None:
    session = SessionLocal()

    # New sample users
    user1 = User(
        username="amal23",
        password="OERGHA80FY9qhiwg",
        first_name="amal",
        last_name="khan",
        email="amal@example.com",
        location="United Kingdom",
        is_verified=True,
    )
    user2 = User(
        closedChats=[1],
        username="ben01",
        password="£*RRYwehif0w9h8",
        first_name="ben",
        last_name="smith",
        email="ben@example.com",
        location="Japan",
        is_verified=True,
    )
    user3 = User(
        closedChats=[3, 7, 11],
        username="c1ndy",
        password="iguf87we",
        first_name="cindy",
        last_name="johnson",
        email="c1ndy@example.com",
        location="Australia",
        is_verified=True,
    )
    user4 = User(
        username="dugg",
        password="*$%&YirhgIOG89",
        first_name="douglas",
        last_name="black",
        email="dugg@example.com",
        location="France",
        is_verified=True,
    )
    session.add_all([user1, user2, user3, user4])
    session.commit()

    # New sample chat history
    chats = [
        ChatHistory(
            convo_id=1, user_id=user1.id, message="I stubbed my toe", sender="user"
        ),
        ChatHistory(
            convo_id=1,
            user_id=user1.id,
            message="See a GP if your pain carries on for more than 3 days",
            sender="assistant",
        ),
        ChatHistory(
            convo_id=2,
            user_id=user2.id,
            message="I have a hole in my side",
            sender="user",
        ),
        ChatHistory(
            convo_id=2,
            user_id=user2.id,
            message="I suggest you call 999",
            sender="assistant",
        ),
        ChatHistory(
            convo_id=13,
            user_id=user3.id,
            message="I'm feeling a bit down today",
            sender="user",
        ),
        ChatHistory(
            convo_id=13,
            user_id=user3.id,
            message="Mental health is important. Do you want to talk about it?",
            sender="assistant",
        ),
        ChatHistory(
            convo_id=1,
            user_id=user4.id,
            message="I'm not sure what to do about my knee",
            sender="user",
        ),
        ChatHistory(
            convo_id=1,
            user_id=user4.id,
            message="Have you thought about getting more exercise?",
            sender="assistant",
        ),
    ]
    session.add_all(chats)
    session.commit()

    # New sample background jobs
    job1 = BackgroundJobs(
        task_id="job_1",
        user_id=user1.id,
        title="Process user data",
        payload={"user_id": user1.id},
        status="success",
    )
    job2 = BackgroundJobs(
        task_id="job_2",
        user_id=user2.id,
        title="Generate report",
        payload={"user_id": user2.id},
        status="pending",
    )
    job3 = BackgroundJobs(
        task_id="job_3",
        user_id=user3.id,
        title="Send notification",
        payload={"user_id": user3.id},
        status="failed",
        error="Notification service unavailable",
    )
    job4 = BackgroundJobs(
        task_id="job_4",
        user_id=user4.id,
        title="Data backup",
        payload={"user_id": user4.id},
        status="running",
    )
    job5 = BackgroundJobs(
        task_id="job_5",
        user_id=user1.id,
        title="Email verification",
        payload={"email": user1.email},
        status="success",
    )
    job6 = BackgroundJobs(
        task_id="job_6",
        user_id=user3.id,
        title="Password reset",
        payload={"user_id": user3.id},
        status="pending",
    )
    session.add_all([job1, job2, job3, job4, job5, job6])
    session.commit()
    session.close()
    print("Seeding complete!")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    seed()
