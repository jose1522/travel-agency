from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict


class CreditCard(BaseModel):
    number: int
    month: int
    year: int
    cvv: int
    issuer: str
    card_type: str


class Transaction(CreditCard):
    amount: float


class UserParams(BaseModel):
    username: str
    password: str


class UserUpdateParams(UserParams):
    username: Optional[str]
    password: Optional[str]
    isAdmin: Optional[bool]


class UserInfoParams(BaseModel):
    identification: Optional[str]
    first_name: str
    last_name: str
    second_last_name: str
    email: str
    birthday: Optional[date]
    phone: Optional[str]


class UserInfoGetOutput(BaseModel):
    identification: Optional[str]
    first_name: str
    last_name: str
    second_last_name: Optional[str]
    email: str
    birthday: Optional[str]
    phone: Optional[str]
    _createdOn: dict
    _active: bool
    _id: str


class NewUserParams(UserInfoParams, UserParams):
    pass


class TokenParams(BaseModel):
    access_token: str
    token_type: str


class NewHotelParams(BaseModel):
    name: str
    email: str
    address: str
    point: Optional[List[float]]
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


class RoomParams(BaseModel):
    id: str


class RoomUpdateParams(NewRoomParams):
    id: str
    number: Optional[int]
    available: Optional[bool]


class NewRoomReservationParams(BaseModel):
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


class NewCarBrandParams(BaseModel):
    name: str
    origin_country: str


class CarBrandParams(NewCarBrandParams):
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


class NewCarModelParams(BaseModel):
    name: str
    brand: str


class CarModelParams(NewCarModelParams):
    id: str


class NewCarReservationParams(BaseModel):
    car: str
    start: date
    end: date


class CarReservationParams(NewCarReservationParams):
    id: str


class NewReservationParams(BaseModel):
    hotel_reservation: List[str]
    car_reservation: List[str]
    total: float
    paid: Optional[bool]


class ReservationParamsParams(NewReservationParams):
    id: str


class ObjectID(BaseModel):
    id: str


class Coordinates(BaseModel):
    lat: int
    lon: int
