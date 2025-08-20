from pydantic import BaseModel, EmailStr
from typing import Optional


class ResearchResponse(BaseModel):
    summary: str
    symptoms: list[str]
    do: list[str]
    dont: list[str]
    gp: list[str]
    sources: list[str]
    assistance: str


class QueryModel(BaseModel):
    query: str
    user_id: int
    convo_id: int | None = None


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    location: Optional[str] = None
    is_verified: bool = False


class UserLogin(BaseModel):
    username: str
    password: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# Model for creating a conversation
class ConversationCreate(BaseModel):
    user_id: int
    title: str
