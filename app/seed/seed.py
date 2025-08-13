import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set! Check your .env file.")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# Define tables (matching your MySQL schema)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True)
    email = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP, default=datetime.now)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    sender = Column(Enum("user", "assistant"))
    timestamp = Column(TIMESTAMP, default=datetime.now)


# Seeder function
def seed():
    session = SessionLocal()

    # Create sample users
    user1 = User(username="sana", email="sana@example.com")
    user2 = User(username="bilal", email="bilal@example.com")
    session.add_all([user1, user2])
    session.commit()

    # Add sample chat history
    chats = [
        ChatHistory(user_id=user1.id, message="abcd", sender="user"),
        ChatHistory(user_id=user1.id, message="efgh", sender="assistant"),
        ChatHistory(user_id=user2.id, message="ijkl", sender="user"),
        ChatHistory(user_id=user2.id, message="mnop", sender="assistant"),
    ]
    session.add_all(chats)
    session.commit()
    session.close()
    print("Seeding complete!")


if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(engine)
    seed()
