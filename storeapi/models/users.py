from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int | None = None
    email: str


class UserIn(User):
    password: str
