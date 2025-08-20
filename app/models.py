from pydantic import BaseModel
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


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    location: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str
