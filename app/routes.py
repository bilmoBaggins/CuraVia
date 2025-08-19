from fastapi import APIRouter, status
from models import QueryModel, UserCreate, UserLogin
from models_db import User
from memory import SessionLocal, load_memory, history_to_db, newUser_to_db, clear_guest_memory
from agent import create_agent, format_memory_to_string
from utils import save_to_txt, save_to_cache
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import jwt  # type: ignore

load_dotenv()  # Loads variables from .env

router = APIRouter()


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("JWT_SECRET_KEY environment variable is not set.")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + expires_delta})
    return jwt.encode(to_encode, str(SECRET_KEY), algorithm="HS256")




@router.post("/ask")
async def ask_question(body: QueryModel):
    if body.user_id == 0:
        clear_guest_memory()
    memory = load_memory(body.user_id)
    agent_executor, parser = create_agent(memory)

    # Format chat history string from memory for prompt input
    chat_history_str = format_memory_to_string(memory)

    raw_response = await agent_executor.ainvoke(
        {"query": body.query, "chat_history": chat_history_str}
    )

    # Default output in case parsing fails
    formatted_output = ""
    try:
        output_text = raw_response.get("output") or raw_response.get("output_text", "")
        try:
            structured_response = parser.parse(output_text)

            formatted_output = structured_response.summary
            if structured_response.symptoms:
                formatted_output += "\n\nCommon symptoms:\n- " + "\n- ".join(
                    structured_response.symptoms
                )
            if structured_response.do:
                formatted_output += "\n\nDo's:\n- " + "\n- ".join(
                    structured_response.do
                )
            if structured_response.dont:
                formatted_output += "\n\nDon'ts:\n- " + "\n- ".join(
                    structured_response.dont
                )
            if structured_response.gp:
                formatted_output += "\n\nWhen to see a GP:\n- " + "\n- ".join(
                    structured_response.gp
                )
            if structured_response.sources:
                formatted_output += "\n\nSources:\n- " + "\n- ".join(
                    structured_response.sources
                )
            if structured_response.assistance:
                formatted_output += (
                    f"\n\n--------------------\n\n{structured_response.assistance}"
                )
        except Exception:
            # fallback if parsing fails
            formatted_output = output_text.strip()

    except Exception as e:
        formatted_output = f"Error parsing response {e}\nRaw response: {raw_response}"

    # Only save history if user_id is not 0 (guest)
    if body.user_id != 0:
        try:
            history_to_db(body.user_id, body.query, formatted_output, datetime.now())
        except Exception as e:
            return {
                "error": f"Failed to save chat history: {e}",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }

        # Optional: still try saving to text/cache but don't block DB insert
        try:
            save_to_txt(formatted_output)
        except Exception as e:
            return {
                "error": f"Failed to save response to text file: {e}",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }

        try:
            save_to_cache(formatted_output)
        except Exception as e:
            return {
                "error": f"Failed to save response to cache: {e}",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }

    return {"message": formatted_output, "status": status.HTTP_200_OK}


@router.post("/signup")
async def signup_user(body: UserCreate):
    session = SessionLocal()
    try:

        existing_user = (
            session.query(User).filter(User.email == body.email).first()
            or session.query(User).filter(User.username == body.username).first()
        )
        if existing_user:
            return {
                "error": "Username or email already used.",
                "status": status.HTTP_409_CONFLICT,
            }

        # Hash the password before storing
        hashed_password = hash_password(body.password)

        newUser_to_db(
            body.username,
            hashed_password,
            body.first_name,
            body.last_name,
            body.email,
            body.location,
        )
        return {
            "message": "User created successfully.",
            "status": status.HTTP_201_CREATED,
        }
    except Exception as e:
        return {
            "error": f"Failed to create new user: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


@router.post("/login")
async def login_user(body: UserLogin):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == body.username).first()
        if not user:
            return {"error": "User not found.", "status": status.HTTP_404_NOT_FOUND}
        else:
            if verify_password(body.password, user.password):
                access_token = create_access_token(
                    {"sub": user.username, "user_id": user.id}
                )
                return {
                    "message": "Login successful.",
                    "access_token": access_token,
                    "status": status.HTTP_200_OK,
                    "user": {
                        "user_id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                    },
                }
            else:
                return {
                    "error": "Invalid password.",
                    "status": status.HTTP_401_UNAUTHORIZED,
                }
    except Exception as e:
        return {
            "error": f"Login failed: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
