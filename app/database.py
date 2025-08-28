import os
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set! Check your .env file.")

# Engine & session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Redis settings
REDIS_URL = os.getenv("REDIS_URL")
REDIS_EXPIRATION_SECONDS = int(os.getenv("REDIS_EXPIRATION_SECONDS"))
redis_client = redis.Redis.from_url(REDIS_URL)
