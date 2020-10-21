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
    birthday: str
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


class NewRoomTypeParams(BaseModel):
    name: str
    hotel: str
    amenities: List[str]
    price: float
    capacity: Optional[int]
    description: Optional[str]


class RoomTypeParams(NewRoomTypeParams):
    id: str


class NewRoomParams(BaseModel):
    hotel: str
    number: int
    room_type: str
    available: Optional[bool]


class RoomParams(NewRoomParams):
    id: str


class NewRoomReservationParams(BaseModel):
    user: str
    room: str
    start: date
    end: date


class RoomReservationParams(NewRoomReservationParams):
    id: str


class NewCarTypeParams(BaseModel):
    name: str
    drive: str
    category: str
    engine: str
    capacity: int


class CarTypeParams(NewCarTypeParams):
    id: str


class NewCarParams(BaseModel):
    brand: str
    model: str
    car_type: str
    color: str
    year: int
    millage: float
    license_plate: str
    available: Optional[bool]


class CarParams(NewCarParams):
    id: str


class ObjectID(BaseModel):
    id: str


class Coordinates(BaseModel):
    lat: int
    lon: int