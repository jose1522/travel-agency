from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from settings import settings
from api.messages import AuthMessage
from api.validation import *
from database import model
import bcrypt

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_hash(password: str):
    password = password.encode('utf8')
    password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf8')
    return password


async def check_password(inputCredentials: dict):
    msg = AuthMessage()

    # get user by username
    inputPassword = inputCredentials.get('password').encode('utf8')
    user = await model.User.searchUsername(inputCredentials.get('username'), include_pwd=True)
    if user:
        userPassword = user.get('password').encode('utf8')

        # check passwords
        result = bcrypt.checkpw(inputPassword, userPassword)
        msg.authResult(result)

        # add token if the passwords match
        if result:
            user = {'username': user.get("username",None)}
            token = create_access_token(user)
            msg.addMessage('Token', token)
    else:
        raise credentials_exception
    return msg


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ENCRYPTION_KEY, algorithm=settings.ENCRYPTION_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str) -> dict:
    try:
        data = jwt.decode(token, settings.ENCRYPTION_KEY, algorithms=[settings.ENCRYPTION_ALGORITHM])
        username: str = data.get("username")
        user = await model.User.searchUsername(username)
        # user = await model.User.searchUserDecrypt(username)
        # return user[0]
        return user
    except JWTError:
        raise credentials_exception


