from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict


class UserParams(BaseModel):
    username: str
    password: str


class UserInfoParams(BaseModel):
    identification: str
    full_name: str
    email: str
    birthday: date
    phone: str


class UserInfoGetOutput(BaseModel):
    identification: str
    full_name: str
    email: str
    birthday: date
    phone: str
    _createdOn: dict
    _active: bool
    _id: str


class TokenParams(BaseModel):
    access_token: str
    token_type: str


class NewHotelParams(BaseModel):
    name: str
    email: str
    address: str
    point: List[float]
    phone: str
    rating: int


class HotelParams(NewHotelParams):
    id: str


class NewRoomType(BaseModel):
    name: str
    hotel: str
    amenities: List[str]
    price: float
    capacity: Optional[int]
    description: Optional[str]


class RoomType(NewRoomType):
    id: str


class ObjectID(BaseModel):
    id: str


class Coordinates(BaseModel):
    lat: int
    lon: int