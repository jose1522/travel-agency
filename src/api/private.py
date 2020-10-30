from fastapi import APIRouter, Depends, Path, Query, Request
from typing import Dict
from api.validation import *
from database import model
from core.security.router_dependencies import check_jwt, check_admin_jwt
from payment import gateway
private = APIRouter()


################################################################
# User-related endpoints
################################################################
@private.get('/user', tags=['User'])
async def get_user(user=Depends(check_jwt)):
    return user


@private.put('/user', tags=['User'])
async def update_user(data: UserUpdateParams, user=Depends(check_jwt)):
    tempData = {}
    for key, value in dict(data).items():
        if value is not None:
            tempData[key] = value
    result = await model.User.updateRecord(user, tempData)
    return result


@private.delete('/user', tags=['User'])
async def delete_user(user=Depends(check_jwt)):
    result = await model.User.deleteRecord(user)
    return result


################################################################
# User-related endpoints
################################################################
@private.post('/user-info', tags=['User Info'])
async def new_user_info(data: UserInfoParams, user=Depends(check_jwt)):
    result = await model.UserInfo.createRecord(data, user)
    return result


@private.get('/user-info', tags=['User Info'], response_model=UserInfoGetOutput)
async def get_user_info(user=Depends(check_jwt)):
    result = await model.UserInfo.searchUsername(user)
    return result


@private.put('/user-info', tags=['User Info'])
async def update_user_info(data: UserInfoParams, user=Depends(check_jwt)):
    result = await model.UserInfo.updateRecord(user, data)
    return result


@private.delete('/user-info', tags=['User Info'])
async def delete_user_info(user=Depends(check_jwt)):
    result = await model.UserInfo.deleteRecord(user['id'])
    return result


################################################################
# Hotel-related endpoints
################################################################
@private.post('/hotel', tags=['Hotel'])
async def new_hotel(data: NewHotelParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.Hotel.createRecord(**data)
    return result


@private.get('/hotel', tags=['Hotel'])
async def get_hotel(
        hotel_id: Optional[str] = Query(None, alias="id", title="Hotel ID", min_length=5),
        geo: Optional[str] = Query(None, title="Geographical Coordinates",
                                   regex="^(-?\d+(\.\d+)?)\'(-?\d+(\.\d+)?)\'(\d+(\.\d+)?)$"),
        name: Optional[str] = Query(None, title="Hotel name", min_length=5),
        skip: Optional[int] = Query(None, title="Skip (n) results"),
        limit: Optional[int] = Query(None, title="Limit to (n) results"),
        user=Depends(check_jwt)
):
    kwargs = {}
    if hotel_id:
        kwargs["id"] = hotel_id
    if geo:
        coordinates = list(map(float, geo.split("'")))
        kwargs["point__near"] = [coordinates[0], coordinates[1]]
        kwargs["point__max_distance"] = coordinates[2]
    if name:
        kwargs["name__icontains"] = name

    result = await model.Hotel.searchWithParams(skip, limit, **kwargs)
    return result


@private.put('/hotel', tags=['Hotel'])
async def update_hotel(data: HotelParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.Hotel.updateRecord(**data)
    return result


@private.delete('/hotel', tags=['Hotel'])
async def delete_hotel(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.Hotel.deleteRecord(data.id)
    return result


################################################################
# Room Type endpoints
################################################################
@private.post('/room-type', tags=['Room Type'])
async def new_room_type(data: NewRoomTypeParams, user=Depends(check_admin_jwt)):
    result = await model.RoomType.createRecord(data)
    return result


@private.get('/room-type', tags=['Room Type'])
async def get_room_type(user=Depends(check_jwt),
                        room_id: Optional[str] = Query(None, alias="id", title="Room Type ID", min_length=5),
                        hotel_id: Optional[str] = Query(None, title="Hotel ID", min_length=5),
                        name: Optional[str] = Query(None, title="Room type name", min_length=5),
                        skip: Optional[int] = Query(None, title="Skip (n) results"),
                        limit: Optional[int] = Query(None, title="Limit to (n) results"),
                        expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")
                        ):
    kwargs = {}
    if room_id:
        kwargs["id"] = room_id
    if hotel_id:
        kwargs["hotel"] = hotel_id
    if name:
        kwargs["name__icontains"] = name

    result = await model.RoomType.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/room-type', tags=['Room Type'])
async def update_room_type(data: RoomTypeParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.RoomType.updateRecord(**data)
    return result


@private.delete('/room-type', tags=['Room Type'])
async def delete_room_type(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.RoomType.deleteRecord(data.id)
    return result


################################################################
# Room endpoints
################################################################
@private.post('/room', tags=['Room'])
async def new_room(data: NewRoomParams, user=Depends(check_admin_jwt)):
    result = await model.Room.createRecord(data)
    return result


@private.get('/room', tags=['Room'])
async def get_room(user=Depends(check_jwt),
                   room_id: Optional[str] = Query(None, alias="id", title="Room ID", min_length=5),
                   hotel_id: Optional[str] = Query(None, title="Hotel ID", min_length=5),
                   room_type_id: Optional[str] = Query(None, title="Room Type ID", min_length=5),
                   number: Optional[int] = Query(None, title="Room number"),
                   skip: Optional[int] = Query(None, title="Skip (n) results"),
                   limit: Optional[int] = Query(None, title="Limit to (n) results"),
                   expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")
                   ):
    kwargs = {'available': True}
    if room_id:
        kwargs["id"] = room_id
    if hotel_id:
        kwargs["hotel"] = hotel_id
    if room_type_id:
        kwargs["room_type"] = room_type_id
    if number:
        kwargs["number"] = room_type_id

    result = await model.Room.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/room', tags=['Room'])
async def update_room(data: RoomUpdateParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.Room.updateRecord(**data)
    return result


@private.delete('/room', tags=['Room'])
async def delete_room(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.Room.deleteRecord(data.id)
    return result


################################################################
# Room Reservation endpoints
################################################################
@private.post('/room-reservation', tags=['Room Reservation'])
async def new_room_reservation(data: NewRoomReservationParams, user=Depends(check_admin_jwt)):
    result = await model.RoomReservation.createRecord(data, user)
    return result


@private.get('/room-reservation', tags=['Room Reservation'])
async def get_room_reservation(user=Depends(check_jwt),
                               room_reservation_id: Optional[str] = Query(None, alias="id", title="Room ID",
                                                                          min_length=5),
                               room_id: Optional[str] = Query(None, title="Room Type ID", min_length=5),
                               skip: Optional[int] = Query(None, title="Skip (n) results"),
                               limit: Optional[int] = Query(None, title="Limit to (n) results"),
                               expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")
                               ):
    kwargs = {"user": user['id']}
    if room_reservation_id:
        kwargs["id"] = room_reservation_id
    if room_id:
        kwargs["room"] = room_id

    result = await model.RoomReservation.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/room-reservation', tags=['Room Reservation'])
async def update_room_reservation(data: RoomReservationParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.RoomReservation.updateRecord(**data)
    return result


@private.delete('/room-reservation', tags=['Room Reservation'])
async def delete_room_reservation(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.RoomReservation.deleteRecord(data.id)
    return result


################################################################
# Car Type endpoints
################################################################
@private.post('/car-type', tags=['Car Type'])
async def new_car_type(data: NewCarTypeParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.CarType.createRecord(**data)
    return result


@private.get('/car-type', tags=['Car Type'])
async def get_car_type(user=Depends(check_jwt),
                       car_type_id: Optional[str] = Query(None, alias="id", title="Car Type Id", min_length=5),
                       name: Optional[str] = Query(None, title="Car Type Name", min_length=5),
                       drive: Optional[str] = Query(None, title="Car Type Drive", min_length=3),
                       category: Optional[str] = Query(None, title="Car Type Category", min_length=5),
                       engine: Optional[str] = Query(None, title="Car Type Engine", min_length=5),
                       skip: Optional[int] = Query(None, title="Skip (n) results"),
                       limit: Optional[int] = Query(None, title="Limit to (n) results"),
                       ):
    kwargs = {}
    if car_type_id:
        kwargs["id"] = car_type_id
    if name:
        kwargs["name"] = name
    if drive:
        kwargs["drive"] = drive
    if category:
        kwargs["category"] = category
    if engine:
        kwargs["engine"] = engine

    result = await model.CarType.searchWithParams(skip, limit, **kwargs)
    return result


@private.put('/car-type', tags=['Car Type'])
async def update_car_type(data: CarTypeParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.CarType.updateRecord(**data)
    return result


@private.delete('/car-type', tags=['Car Type'])
async def delete_car_type(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.CarType.deleteRecord(data.id)
    return result


################################################################
# Car Brand endpoints
################################################################
@private.post('/car-brand', tags=['Car Brand'])
async def new_car_brand(data: NewCarBrandParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.CarBrand.createRecord(**data)
    return result


@private.get('/car-brand', tags=['Car Brand'])
async def get_car_brand(user=Depends(check_jwt),
                        car_brand_id: Optional[str] = Query(None, alias="id", title="Car Brand ID", min_length=5),
                        name: Optional[str] = Query(None, title="Car Brand Name", min_length=5),
                        country: Optional[str] = Query(None, title="Car Brand Country", min_length=5),
                        skip: Optional[int] = Query(None, title="Skip (n) results"),
                        limit: Optional[int] = Query(None, title="Limit to (n) results")
                        ):
    kwargs = {}
    if car_brand_id:
        kwargs["id"] = car_brand_id
    if name:
        kwargs["name"] = name
    if country:
        kwargs["origin_country"] = country

    result = await model.CarBrand.searchWithParams(skip, limit, **kwargs)
    return result


@private.put('/car-brand', tags=['Car Brand'])
async def update_car_brand(data: CarBrandParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.CarBrand.updateRecord(**data)
    return result


@private.delete('/car-brand', tags=['Car Brand'])
async def delete_car_brand(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.CarBrand.deleteRecord(data.id)
    return result


################################################################
# Car Model endpoints
################################################################
@private.post('/car-model', tags=['Car Model'])
async def new_car_model(data: NewCarModelParams, user=Depends(check_admin_jwt)):
    result = await model.CarModel.createRecord(data)
    return result


@private.get('/car-model', tags=['Car Model'])
async def get_car_model(user=Depends(check_jwt),
                        car_brand_id: Optional[str] = Query(None, alias="id", title="Car Brand ID", min_length=5),
                        name: Optional[str] = Query(None, title="Car Model Name", min_length=5),
                        brand: Optional[str] = Query(None, title="Car Model Brand", min_length=5),
                        skip: Optional[int] = Query(None, title="Skip (n) results"),
                        limit: Optional[int] = Query(None, title="Limit to (n) results"),
                        expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")):
    kwargs = {}
    if car_brand_id:
        kwargs["id"] = car_brand_id
    if name:
        kwargs["name"] = name
    if brand:
        kwargs["brand"] = brand

    result = await model.CarModel.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/car-model', tags=['Car Model'])
async def update_car_model(data: CarModelParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.CarModel.updateRecord(**data)
    return result


@private.delete('/car-model', tags=['Car Model'])
async def delete_car_model(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.CarModel.deleteRecord(data.id)
    return result


################################################################
# Car endpoints
################################################################
@private.post('/car', tags=['Car'])
async def new_car(data: NewCarParams, user=Depends(check_admin_jwt)):
    result = await model.Car.createRecord(data)
    return result


@private.get('/car', tags=['Car'])
async def get_car(user=Depends(check_jwt),
                  car_id: Optional[str] = Query(None, alias="id", title="Car ID", min_length=5),
                  model_id: Optional[str] = Query(None, title="Car Model", min_length=5),
                  color: Optional[str] = Query(None, title="Car Color", min_length=3),
                  car_type: Optional[str] = Query(None, title="Car Model Brand", min_length=5),
                  skip: Optional[int] = Query(None, title="Skip (n) results"),
                  limit: Optional[int] = Query(None, title="Limit to (n) results"),
                  expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")):
    kwargs = {}
    if car_id:
        kwargs["id"] = car_id
    if model_id:
        kwargs["model"] = model_id
    if color:
        kwargs["color"] = color
    if car_type:
        kwargs["car_type"] = car_type

    result = await model.Car.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/car', tags=['Car'])
async def update_car(data: CarParams, user=Depends(check_admin_jwt)):
    data = dict(data)
    result = await model.Car.updateRecord(**data)
    return result


@private.delete('/car', tags=['Car'])
async def delete_car(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.Car.deleteRecord(data.id)
    return result


################################################################
# Car Reservation endpoints
################################################################
@private.post('/car-reservation', tags=['Car Reservation'])
async def new_car_reservation(data: NewCarReservationParams, user=Depends(check_admin_jwt)):
    result = await model.CarReservation.createRecord(data, user)
    return result


@private.get('/car-reservation', tags=['Car Reservation'])
async def get_car_reservation(user=Depends(check_jwt),
                              car_id: Optional[str] = Query(None, alias="id", title="Car Brand ID", min_length=5),
                              car: Optional[str] = Query(None, title="Car Brand ID", min_length=5),
                              skip: Optional[int] = Query(None, title="Skip (n) results"),
                              limit: Optional[int] = Query(None, title="Limit to (n) results"),
                              expand_field: Optional[List[str]] = Query(None, title="Show expanded field data")):
    kwargs = {}
    if car_id:
        kwargs["id"] = car_id
    if user:
        kwargs["user"] = user['id']
    if car:
        kwargs["car"] = car

    result = await model.CarReservation.searchWithParams(skip, limit, expand=expand_field, **kwargs)
    return result


@private.put('/car-reservation', tags=['Car Reservation'])
async def update_car_reservation(data: CarReservationParams, user=Depends(check_jwt)):
    data = dict(data)
    result = await model.CarReservation.updateRecord(**data)
    return result


@private.delete('/car-reservation', tags=['Car Reservation'])
async def delete_car_reservation(data: ObjectID, user=Depends(check_jwt)):
    result = await model.CarReservation.deleteRecord(data.id)
    return result


################################################################
# Reservation endpoints
################################################################
@private.post('/reservation', tags=['Reservation'])
async def new_reservation(data: NewReservationParams, user=Depends(check_admin_jwt)):
    result = await model.Reservation.createRecord(data, user)
    return result


@private.get('/reservation', tags=['Reservation'])
async def get_reservation(user=Depends(check_jwt),
                          reservation: Optional[str] = Query(None, alias="id", title="Car Brand ID", min_length=5),
                          skip: Optional[int] = Query(None, title="Skip (n) results"),
                          limit: Optional[int] = Query(None, title="Limit to (n) results")
                          ):
    kwargs = {}
    if reservation:
        kwargs["id"] = reservation
    result = await model.Reservation.searchWithParams(skip, limit, **kwargs)
    return result


@private.put('/reservation', tags=['Reservation'])
async def update_reservation(data: ReservationParamsParams, user=Depends(check_jwt)):
    data = dict(data)
    result = await model.Reservation.updateRecord(**data)
    return result


@private.delete('/reservation', tags=['Reservation'])
async def delete_reservation(data: ObjectID, user=Depends(check_jwt)):
    result = await model.Reservation.deleteRecord(data.id)
    return result


################################################################
# Payment endpoints
################################################################
@private.post('/transaction/', tags=['Payment Gateway'])
async def index(item: gateway.Transaction,  user=Depends(check_jwt)):
    verification = gateway.Verification(item)
    response = {}
    if verification.verifyCard():
        authorization = gateway.Authorization(item)
        authorization.processTransaction()
        response = authorization.data
    else:
        response = verification.data
    return response
