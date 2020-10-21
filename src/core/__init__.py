from fastapi import FastAPI, Depends, Request
from mongoengine import DoesNotExist, ValidationError
from fastapi.responses import JSONResponse
from api.private import private
from api.public import public
from core.security.router_dependencies import *


def create_app():
    app = FastAPI(title="Travel Agency", version="0.1")
    app.include_router(private,
                       prefix='/secure',
                       dependencies=[Depends(check_jwt)],
                       responses={404: {"description": "Not found"}})
    app.include_router(public,
                       tags=['Public'],
                       responses={404: {"description": "Not found"}})

    @app.exception_handler(DoesNotExist)
    async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
        return JSONResponse(
            status_code=204,
            content={"message": f"Oops! Your query didn't return any results"},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"message": f"Oops! It looks like the information received didn't have the correct format."},
        )

    return app
