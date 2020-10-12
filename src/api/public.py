from __future__ import absolute_import
from fastapi import APIRouter, Path
from api.validation import *
from database import model


public = APIRouter()


@public.post('/authenticate')
async def authenticate(user: UserParams):
    result = await model.User.authenticate(user)
    return result


@public.post('/user')
async def new_user(user: UserParams):
    result = await model.User.createUser(user)
    return result


@public.get('/test')
async def test():
    result = await model.User.testSearch()
    return result
