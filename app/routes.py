from fastapi import APIRouter, status, Request, Body
from models import (
    UserCreate,
    UserLogin,
    ConversationCreate,
    QueryModel,
    ResendVerificationRequest,
)
from controllers.query_controller import ask_question_logic
from controllers.user_controller import (
    signup_user_logic,
    login_user_logic,
    verify_email_logic,
    send_verification_email_logic,
    resend_verification_email_logic,
)
from controllers.conversation_controller import (
    get_conversations_logic,
    create_conversation_logic,
    get_messages_logic,
    get_closed_chats_logic,
    add_closed_chat_logic,
)


router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to CuraVia API", "status": status.HTTP_200_OK}


@router.post("/ask")
async def ask_question(body: QueryModel):
    return await ask_question_logic(body)


@router.post("/signup")
async def signup_user(body: UserCreate):
    return await signup_user_logic(body)


@router.post("/login")
async def login_user(body: UserLogin):
    return await login_user_logic(body)


@router.get("/verify")
async def verify_email(token: str):
    return await verify_email_logic(token)


# New endpoint to send verification email directly
@router.post("/send-verification-email")
async def send_verification_email(request: Request):
    return await send_verification_email_logic(request)


@router.post("/resend-verification-email")
async def resend_verification_email(body: ResendVerificationRequest):
    return await resend_verification_email_logic(body)


@router.get("/conversations")
async def get_conversations(user_id: int):
    return await get_conversations_logic(user_id)


@router.post("/conversations")
async def create_conversation(body: ConversationCreate):
    return await create_conversation_logic(body)


@router.get("/messages")
async def get_messages(conversation_id: int, user_id: int):
    return await get_messages_logic(conversation_id, user_id)


# Get closedChats for a user
@router.get("/users/{user_id}/closed_chats")
async def get_closed_chats(user_id: int):
    return await get_closed_chats_logic(user_id)


# Add a convo_id to closedChats for a user
@router.post("/users/{user_id}/closed_chats")
async def add_closed_chat(user_id: int, data: dict = Body(...)):
    return await add_closed_chat_logic(user_id, data)
