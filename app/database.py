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
if REDIS_URL is None:
    raise ValueError("REDIS_URL not set! Check your .env file.")

REDIS_EXPIRATION_SECONDS_RAW = os.getenv("REDIS_EXPIRATION_SECONDS")
if REDIS_EXPIRATION_SECONDS_RAW is None:
    raise ValueError("REDIS_EXPIRATION_SECONDS not set! Check your .env file.")
REDIS_EXPIRATION_SECONDS = int(REDIS_EXPIRATION_SECONDS_RAW)

redis_client = redis.Redis.from_url(REDIS_URL)
