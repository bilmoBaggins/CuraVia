import os
from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
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


# User table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)


# ChatHistory table
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    sender: Mapped[str] = mapped_column(Enum("user", "assistant"))
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)


# Seeder function
def seed() -> None:
    session = SessionLocal()

    # New sample users
    user1 = User(
        username="amal23",
        password="amalamal",
        first_name="amal",
        last_name="khan",
        email="amal@example.com",
        location="London",
    )
    user2 = User(
        username="ben01",
        password="benneb1",
        first_name="ben",
        last_name="smith",
        email="ben@example.com",
        location="Japan",
    )
    session.add_all([user1, user2])
    session.commit()

    # New sample chat history
    chats = [
        ChatHistory(user_id=user1.id, message="I stubbed my toe", sender="user"),
        ChatHistory(
            user_id=user1.id,
            message="See a GP if your pain carries on for more than 3 days",
            sender="assistant",
        ),
        ChatHistory(
            user_id=user2.id, message="I have a hole in my side", sender="user"
        ),
        ChatHistory(user_id=user2.id, message="I suggest you call 999", sender="assistant"),
    ]
    session.add_all(chats)
    session.commit()
    session.close()
    print("Seeding complete!")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    seed()
