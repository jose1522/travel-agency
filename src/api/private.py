from fastapi import APIRouter, Depends, Path
from api.validation import *
from database import model
from core.security.router_dependencies import check_jwt

private = APIRouter()


################################################################
# User-related endpoints
################################################################
@private.get('/user', tags=['User'])
async def get_user(user=Depends(check_jwt)):
    return user


@private.put('/user', tags=['User'])
async def update_user(data: UserParams, user=Depends(check_jwt)):
    result = await model.User.updateUser(user, data)
    return result


@private.delete('/user', tags=['User'])
async def delete_user(user=Depends(check_jwt)):
    result = await model.User.deleteUser(user)
    return result

################################################################
# User-related endpoints
################################################################

@private.post('/user-info', tags=['User Info'])
async def new_user(data: UserInfoParams, user=Depends(check_jwt)):
    result = await model.UserInfo.createUserInfo(data, user)
    return result


@private.get('/user-info', tags=['User Info'])
async def get_user(user=Depends(check_jwt)):
    result = await model.UserInfo.searchUsername(user)
    return result


@private.put('/user-info', tags=['User Info'])
async def update_user(data: UserInfoParams, user=Depends(check_jwt)):
    result = await model.UserInfo.updateUserInfo(user, data)
    return result