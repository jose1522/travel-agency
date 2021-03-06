from fastapi import Header, HTTPException, Depends
from settings import settings
from core.security.authentication import get_current_user, oauth2_scheme

# async def check_token(x_token: str = Header(...)):
#     if x_token != settings.ACCESS_TOKEN:
#         raise HTTPException(status_code=400, detail='X-Token header invalid')


async def check_jwt(token: str = Depends(oauth2_scheme)):
    try:
        data = await get_current_user(token)
        return data
    except Exception as e:
        raise HTTPException(status_code=401, detail='Authentication Error')


async def check_admin_jwt(token: str = Depends(oauth2_scheme)):
    try:
        data = await get_current_user(token)
        if not data.get("isAdmin"):
            raise HTTPException(status_code=403, detail='Access Restricted')
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail='Authentication Error')
