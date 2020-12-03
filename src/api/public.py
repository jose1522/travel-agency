from __future__ import absolute_import
from fastapi import APIRouter, Path, Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.security.authentication import credentials_exception
from api.validation import *
from database import model


public = APIRouter()


@public.post('/token', response_model=TokenParams)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserParams(**form_data.__dict__)
    result = await model.User.authenticate(user)
    if not result.get('Token'):
        raise  credentials_exception
    return {"access_token": result.get("Token"), "token_type": "bearer"}


@public.post('/authenticate')
async def authenticate(user: UserParams):
    result = await model.User.authenticate(user)
    return result


@public.post('/user')
async def new_user(user: NewUserParams):
    userDataFields = list(UserParams.schema().get("properties").keys())
    userInfoDataFields = list(UserInfoParams.schema().get("properties").keys())
    userData = {}
    userInfoData = {}
    for key, value in dict(user).items():
        if key in userDataFields:
            userData[key] = value
        if key in userInfoDataFields:
            userInfoData[key] = value
    result = await model.User.createRecord(userData)
    userID = result.get("Created").get("id")
    userData['id'] = userID
    await model.UserInfo.createRecord(userInfoData, userData)
    return result


@public.get('/test')
async def test():
    result = await model.User.testSearch()
    return result
