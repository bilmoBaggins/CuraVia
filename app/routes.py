import jwt  # type: ignore
from fastapi import APIRouter, status, Request, Body
from models import (
    UserCreate,
    UserLogin,
    ConversationCreate,
    QueryModel,
)
from models_db import User, ChatHistory
from memory import load_memory, history_to_db, newUser_to_db, clear_guest_memory
from agent import create_agent, format_memory_to_string
from database import SessionLocal
from sqlalchemy import desc, func
from utils import (
    save_to_txt,
    save_to_cache,
    SECRET_KEY,
    create_access_token,
    create_verification_token,
    send_verification_email,
)
from datetime import datetime
from passlib.context import CryptContext


router = APIRouter()


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to CuraVia API"}


@router.post("/ask")
async def ask_question(body: QueryModel):

    # Greeting detection
    greetings = [
        "hi",
        "hello",
        "hey",
        "greetings",
        "good morning",
        "good afternoon",
        "good evening",
    ]
    if any(greet in body.query.lower() for greet in greetings):
        return {
            "message": "Hello! I'm CuraVia, your assistant. How can I help you today?",
            "status": status.HTTP_200_OK,
        }

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
    if body.user_id != 0 and body.convo_id:
        try:
            history_to_db(
                body.user_id,
                body.convo_id,
                body.query,
                formatted_output,
                datetime.now(),
            )
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

        token = create_verification_token(body.email)
        send_verification_email(body.email, token)

        return {
            "message": "User created successfully. "
            "Please check your email to verify your account.",
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
            return {
                "error": "Invalid username or password.",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
        if not user.is_verified:
            return {
                "error": "Your account is not verified. "
                "Please check your email and verify your account to log in.",
                "status": status.HTTP_403_FORBIDDEN,
                "resend_verification": True,
                "email": user.email,
            }
        if verify_password(body.password, user.password):
            access_token = create_access_token(
                {"sub": user.username, "user_id": user.id}
            )
            return {
                "message": "Login successful.",
                "status": status.HTTP_200_OK,
                "access_token": access_token,
                "user": {
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "is_verified": user.is_verified,
                },
            }
        else:
            return {
                "error": "Invalid username or password.",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
    except Exception as e:
        return {
            "error": f"Login failed: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


@router.get("/verify")
async def verify_email(token: str):
    session = SessionLocal()
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms="HS256")
        email = payload["sub"]

        # Find user and mark verified
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return {
                "error": "User not found.",
                "status": status.HTTP_404_NOT_FOUND,
            }

        user.is_verified = True
        session.commit()
        return {
            "message": f"Email {email} has been verified!",
            "status": status.HTTP_200_OK,
        }

    except jwt.ExpiredSignatureError:
        return {
            "error": "Verification link expired.",
            "status": status.HTTP_400_BAD_REQUEST,
        }
    except jwt.InvalidTokenError:
        return {
            "error": "Invalid verification token.",
            "status": status.HTTP_400_BAD_REQUEST,
        }


# New endpoint to send verification email directly
@router.post("/send-verification-email")
async def send_verification_email_endpoint(request: Request):
    data = await request.json()
    email = data.get("email")
    if not email:
        return {"error": "Email is required.", "status": status.HTTP_400_BAD_REQUEST}
    from utils import send_verification_email, create_verification_token

    token = create_verification_token(email)
    result = send_verification_email(email, token)
    return result


@router.get("/conversations")
async def get_conversations(user_id: int):
    session = SessionLocal()
    try:
        # Get all unique conversations for this user, ordered by latest timestamp (most recent first)
        convo_ids = (
            session.query(ChatHistory.convo_id, func.max(ChatHistory.timestamp).label("latest"))
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


@router.post("/conversations")
async def create_conversation(body: ConversationCreate):
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


@router.get("/messages")
async def get_messages(conversation_id: int, user_id: int):
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


# Get closedChats for a user
@router.get("/users/{user_id}/closed_chats")
async def get_closed_chats(user_id: int):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.closedChats if user.closedChats else []
    finally:
        session.close()


# Add a convo_id to closedChats for a user
@router.post("/users/{user_id}/closed_chats")
async def add_closed_chat(user_id: int, data: dict = Body(...)):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found", "status": status.HTTP_404_NOT_FOUND}
        convo_id = data.get("convo_id")
        if convo_id is None:
            return {"error": "Missing convo_id", "status": status.HTTP_400_BAD_REQUEST}
        closed = user.closedChats if user.closedChats else []
        if convo_id not in closed:
            closed.append(convo_id)
            user.closedChats = closed
            session.commit()
        return {"closedChats": user.closedChats, "status": status.HTTP_200_OK}
    finally:
        session.close()
