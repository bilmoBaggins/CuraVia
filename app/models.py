from pydantic import BaseModel


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
    first_name: str
    last_name: str
    email: str
    location: str


class UserLogin(BaseModel):
    username: str
    password: str
