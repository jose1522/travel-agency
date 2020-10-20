from mongoengine import *
from api.messages import *
from core.security.authentication import *
from database.controller import CRUD
from database.custom import *
import json


def extractIDValue(data: dict) -> str:
    if not data:
        raise Exception('Id not found')
    return data['_id']['$oid']


def timestampToStr(timestamp: dict) -> str:
    return datetime.fromtimestamp(timestamp['$date'] / 1e3).strftime("%Y-%m-%d")


class User(BaseDocument):
    username = StringField(max_length=120, required=True, unique=True)
    password = PasswordStringField(max_length=120, required=True)
    isAdmin = BooleanField(default=False)

    meta = {
        'indexes': ['username']
    }

    @classmethod
    async def createUser(cls, newUser: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            newUser = dict(newUser)
            crud.create(newUser, msg)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def updateUser(cls, currentUser, newData: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            currentUser = dict(currentUser)
            query = {"username": currentUser.get('username')}
            exclude = ['username', 'id']
            crud.read(query=query)
            crud.update(newData, msg, exclude=exclude)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def deleteUser(cls, currentUser):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            currentUser = dict(currentUser)
            query = {"username": currentUser.get('username'), 'active': True}
            crud.read(query=query)
            crud.delete(msg)
            await UserInfo.deleteUserInfo(crud.documents.id)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def authenticate(cls, inputCredentials: UserParams):
        msg = AuthMessage()
        try:
            msg = await check_password(dict(inputCredentials))
        except Exception as e:
            msg.authResult(False)
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def searchUsername(cls, username: str, include_pwd: bool = False) -> dict:
        data = None
        try:
            query = {"username": username, 'active': True}
            if include_pwd:
                data = cls.query(query=query)
            else:
                data = cls.query(exclude=['password'], query=query)
            if len(data):
                data = data.to_dict()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def searchId(cls, userId: str) -> dict:
        data = None
        try:
            query = {"id": userId, 'active': True}
            data = cls.query(exclude=['password'], query=query)
            data = data.to_dict()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def testSearch(cls):
        data = []
        try:
            query = {"username": 'as'}
            data = cls.query(exclude=['password'], query=query)
            if data:
                data = data.to_dict()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data


class UserInfo(BaseDocument):
    user_id = StringField(unique=True, required=True)
    identification = StringField(required=True, min_length=5, max_length=25)
    full_name = StringField(required=True, max_length=50, min_length=3)
    email = EmailField(required=True, unique=True, min_length=5, max_length=100)
    birthday = DateField(required=True)
    phone = StringField(min_length=5, max_length=20)

    meta = {
        'indexes': ['user_id']
    }

    async def __appendUserID(self, userInfo: UserInfoParams, user: UserParams) -> dict:
        user = dict(user)
        userInfo = dict(userInfo)
        user = await User.searchUsername(user.get('username'))
        if user:
            userInfo['user_id'] = extractIDValue(user)
            return userInfo
        else:
            raise ValueError('Invalid user_id')

    @classmethod
    async def createUserInfo(cls, userInfo: UserInfoParams, user: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            userInfo = await cls.__appendUserID(cls(), userInfo, user)
            crud.create(userInfo, msg)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def searchUsername(cls, user: UserParams) -> dict:
        data = None
        user = dict(user)
        try:
            user = await User.searchUsername(user['username'])
            user = extractIDValue(user)
            query = {"user_id": user, 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
            data['birthday'] = timestampToStr(data['birthday'])
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def searchUserId(cls, user: str) -> dict:
        data = None
        try:
            query = {"user_id": user, 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def searchId(cls, userInfoId: str) -> dict:
        data = None
        try:
            query = {"id": userInfoId, 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def updateUserInfo(cls, user: UserParams, newData: UserInfoParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            user = await cls.__appendUserID(cls(), newData, user)
            query = {"user_id": user.get('user_id'), 'active': True}
            exclude = ['user_id', 'id']
            crud.read(query=query)
            crud.update(newData, msg, exclude=exclude)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def deleteUserInfo(cls, userId: str) -> None:
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"user_id": userId, 'active': True}
            crud.read(query=query)
            crud.delete(msg, softDelete=False)
        except Exception as e:
            raise e


class Hotel(BaseDocument):
    name = StringField(unique=True, required=True)
    email = EmailField(required=True, unique=True, min_length=5, max_length=25)
    address = StringField(required=True, max_length=200, min_length=10)
    point = PointField(required=True)
    phone = StringField(required=True, min_length=5, max_length=15)
    rating = IntField(required=True, max_value=5)

    meta = {
        'indexes': ['$name', 'rating']
    }

    @classmethod
    async def createHotel(cls, newHotel: NewHotelParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            newHotel = dict(newHotel)
            crud.create(newHotel, msg)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def searchHotel(cls, skip, limit, **kwargs) -> dict:
        data = None
        crud = CRUD(cls=cls)
        try:
            kwargs["active"] = True
            crud.read(query=kwargs, skip=skip, limit=limit, exclude=['createdOn', 'active'])
            data = crud.toJSON()
        except Exception as e:
            logging.error(str(e))
        finally:
            return data

    @classmethod
    async def updateHotel(cls, hotel: HotelParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            hotelDict = dict(hotel)
            query = {"id": hotelDict.get('id'), 'active': True}
            exclude = ['id']
            crud.read(query=query)
            crud.update(hotel, msg, exclude=exclude)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data

    @classmethod
    async def deleteHotel(cls, hotelId: str) -> None:
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"id": hotelId, 'active': True}
            crud.read(query=query)
            crud.delete(msg)
        except Exception as e:
            raise e


class RoomType(BaseDocument):
    name = StringField(required=True)
    hotel = ReferenceField(Hotel)
    amenities = ListField()
    price = FloatField(required=True)
    capacity = IntField(default=2, min_value=1, max_value=10)
    description = StringField()

    @classmethod
    async def createRoomType(cls, newRoomType: NewRoomType):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            newRoomType = dict(newRoomType)
            crud.create(newRoomType, msg)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data


class Room(BaseDocument):
    hotel = ReferenceField(Hotel)
    number = IntField(required=True, min_value=1, unique_with=['hotel'])
    room_type = ReferenceField(RoomType)
    available = BooleanField(default=True)
    photos = ListField(ImageField(size=(800, 600, True), thumbnail_size=(100, 75, True)))


class RoomReservation(BaseDocument):
    user = ReferenceField(User)
    room = ReferenceField(Room)
    start = DateField(required=True)
    end = DateField(required=True)


class CarType(BaseDocument):
    name = StringField(required=True)
    drive = StringField(required=True, choices=('4WD', '2WD'))
    category = StringField(required=True, choices=('Hatchback', 'Sedan', 'SUV', 'Compact'))
    engine = StringField(required=True, choices=('Electric', 'Diesel', 'Gasoline'))
    capacity = IntField(default=5)


class Car(BaseDocument):
    make = StringField(required=True)
    license_plate = StringField(required=True)
    car_type = ReferenceField(CarType)
    available = BooleanField(default=True)
    photos = ListField(ImageField(size=(800, 600, True), thumbnail_size=(100, 75, True)))


class CarReservation(BaseDocument):
    user = ReferenceField(User)
    car = ReferenceField(Car)
    start = DateField(required=True)
    end = DateField(required=True)


class Reservation(BaseDocument):
    user = ReferenceField(User)
    hotel_reservation = ListField(ReferenceField(RoomReservation))
    car_reservation = ListField(ReferenceField(CarReservation))
