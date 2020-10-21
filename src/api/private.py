from fastapi import APIRouter, Depends, Path, Query, Request
from typing import Dict
from api.validation import *
from database import model
from core.security.router_dependencies import check_jwt, check_admin_jwt

private = APIRouter()

################################################################
# User-related endpoints
################################################################
@private.get('/user', tags=['User'])
async def get_user(user=Depends(check_jwt)):
    return user


@private.put('/user', tags=['User'])
async def update_user(data: UserParams, user=Depends(check_jwt)):
    result = await model.User.updateRecord(user, data)
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
                    geo: Optional[str] = Query(None, title="Geographical Coordinates", regex="^(-?\d+(\.\d+)?)\'(-?\d+(\.\d+)?)\'(\d+(\.\d+)?)$"),
                    name: Optional[str] = Query(None, title="Hotel name", min_length=5),
                    skip: Optional[int] = Query(None, title="Skip (n) results"),
                    limit: Optional[int] = Query(None, title="Limit to (n) results"),
                    user=Depends(check_jwt)
):
    # result = await model.Hotel.searchHotel(hotel)
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
                        room_id: Optional[str] = Query(None, alias="id", title="Hotel ID", min_length=5),
                        hotel_id: Optional[str] = Query(None, title="Hotel ID", min_length=5),
                        name: Optional[str] = Query(None, title="Hotel name", min_length=5),
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
    result = await model.RoomType.updateRecord(data)
    return result


@private.delete('/room-type', tags=['Room Type'])
async def delete_room_type(data: ObjectID, user=Depends(check_admin_jwt)):
    result = await model.RoomType.deleteRecord(data.id)
    return result