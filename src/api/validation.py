from pydantic import BaseModel
from typing import Optional


class UserParams(BaseModel):
    username: str
    password: str


class UserInfoParams(BaseModel):
    identification: str
    full_name: str
    email: str
    birthday: str
    phone: str


class TokenParams(BaseModel):
    access_token: str
    token_type: str
