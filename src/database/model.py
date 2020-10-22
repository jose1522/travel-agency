from mongoengine import *
from api.messages import *
from core.security.authentication import *
from database.controller import CRUD
from database.custom import *
import json

from mongoengine import *
from api.messages import *
from core.security.authentication import *
from database.controller import CRUD
from database.custom import *
import json


class User(BaseDocument):
    username = StringField(max_length=120, required=True, unique=True)
    password = StringField(max_length=120, required=True)
    isAdmin = BooleanField(default=False)

    meta = {
        'indexes': ['username'],
        'exclude_from_update': ['username', 'password']
    }

    @classmethod
    async def createRecord(cls, newUser: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            newUser = dict(newUser)
            newUser['password'] = get_hash(newUser['password'])
            crud.create(newUser, msg)
            return msg.data
        except DoesNotExist:
            raise
        except NotUniqueError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def updateRecord(cls, currentUser, newData: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            currentUser = dict(currentUser)
            query = {"username": currentUser.get('username')}
            exclude = cls._meta.get("exclude_from_update", [])
            if 'id' not in exclude:
                exclude.append('id')
            crud.read(query=query)
            crud.update(newData, msg, exclude=exclude)
            return msg.data
        except DoesNotExist:
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


    @classmethod
    async def deleteRecord(cls, currentUser):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            currentUser = dict(currentUser)
            query = {"username": currentUser.get('username'), 'active': True}
            crud.read(query=query)
            crud.delete(msg)
            await UserInfo.deleteRecord(crud.documents.id)
            return msg.data
        except DoesNotExist:
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def authenticate(cls, inputCredentials: UserParams):
        msg = AuthMessage()
        try:
            msg = await check_password(dict(inputCredentials))
        except Exception as e:
            msg.authResult(False)
        finally:
            return msg.data

    @classmethod
    async def searchUsername(cls, username: str, include_pwd: bool = False) -> dict:
        try:
            query = {"username": username, 'active': True}
            if include_pwd:
                data = cls.query(query=query)
            else:
                data = cls.query(exclude=['password'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def searchId(cls, userId: str) -> dict:
        try:
            query = {"id": userId, 'active': True}
            data = cls.query(exclude=['password'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def testSearch(cls):
        try:
            query = {"username": 'as'}
            data = cls.query(exclude=['password'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise


class UserInfo(BaseDocument):
    user_id = StringField(unique=True, required=True)
    identification = StringField(required=True, min_length=5, max_length=25)
    full_name = StringField(required=True, max_length=50, min_length=3)
    email = EmailField(required=True, unique=True, min_length=5, max_length=100)
    birthday = DateField(required=True)
    phone = StringField(min_length=5, max_length=20)

    meta = {
        'indexes': ['user_id'],
        'exclude_from_update': ['user_id', 'id']
    }

    @classmethod
    async def createRecord(cls, userInfo: UserInfoParams, user: UserParams):
        msg = Message()
        crud = CRUD(cls=cls)
        user = dict(user)
        try:
            userInfo = dict(userInfo)
            userInfo['user_id'] = user['id']
            crud.create(userInfo, msg)
            return msg.data
        except DoesNotExist:
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def searchUsername(cls, user: UserParams) -> dict:
        user = dict(user)
        try:
            user = await User.searchUsername(user['username'])
            query = {"user_id": user['id'], 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def searchUserId(cls, user: str) -> dict:
        try:
            query = {"user_id": user, 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def searchId(cls, userInfoId: str) -> dict:
        try:
            query = {"id": userInfoId, 'active': True}
            data = cls.query(exclude=['user_id'], query=query)
            data = data.to_dict()
            return data
        except DoesNotExist:
            raise
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def updateRecord(cls, user: UserParams, newData: UserInfoParams):
        msg = Message()
        crud = CRUD(cls=cls)
        user = dict(user)
        try:
            query = {"user_id": user.get('id'), 'active': True}
            exclude = cls._meta.get("exclude_from_update", [])
            if 'id' not in exclude:
                exclude.append('id')
            crud.read(query=query)
            crud.update(newData, msg, exclude=exclude)
            return msg.data
        except DoesNotExist:
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def deleteRecord(cls, userId: str) -> None:
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"user_id": userId, 'active': True}
            crud.read(query=query)
            crud.delete(msg, softDelete=False)
            return msg.data
        except DoesNotExist:
            raise
        except Exception as e:
            raise


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


class RoomType(BaseDocument):
    name = StringField(required=True, unique_with=['hotel'])
    hotel = ReferenceField(Hotel)
    amenities = ListField()
    price = FloatField(required=True)
    capacity = IntField(default=2, min_value=1, max_value=10)
    description = StringField()

    meta = {
        'exclude_from_update': ['hotel', 'id']
    }

    @classmethod
    async def createRecord(cls, newRoomType: NewRoomTypeParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            hotel = model.Hotel.objects.get(id=newRoomType.hotel)
            newRoomType = dict(newRoomType)
            newRoomType['hotel'] = hotel.id
            crud.create(newRoomType, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except NotUniqueError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


class Room(BaseDocument):
    hotel = ReferenceField(Hotel)
    number = IntField(required=True, min_value=1, unique_with=['hotel'])
    room_type = ReferenceField(RoomType)
    available = BooleanField(default=True)
    # photos = ListField(ImageField(size=(800, 600, True), thumbnail_size=(100, 75, True)))

    @classmethod
    async def createRecord(cls, room: NewRoomParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            roomDoc = model.RoomType.objects.get(id=room.room_type)
            hotelDoc = model.Hotel.objects.get(id=room.hotel)
            room = dict(room)
            room['room_type'] = roomDoc.id
            room['hotel'] = hotelDoc.id
            crud.create(room, msg)
        except Exception as e:
            msg.addMessage('Error', str(e))
        finally:
            return msg.data


class RoomReservation(BaseDocument):
    user = ReferenceField(User)
    room = ReferenceField(Room)
    start = DateField(required=True)
    end = DateField(required=True)

    @classmethod
    async def createRecord(cls, room: NewRoomReservationParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            roomDoc = model.Room.objects.get(id=room.room)
            userDoc = model.User.objects.get(id=room.user)
            room = dict(room)
            room['room'] = roomDoc.id
            room['user'] = userDoc.id
            crud.create(room, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except NotUniqueError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


class CarType(BaseDocument):
    name = StringField(required=True)
    drive = StringField(required=True, choices=('4WD', '2WD'))
    category = StringField(required=True, choices=('Hatchback', 'Sedan', 'SUV', 'Compact'))
    engine = StringField(required=True, choices=('Electric', 'Diesel', 'Gasoline'))
    capacity = IntField(default=5)


class CarBrand(BaseDocument):
    name = StringField(required=True)
    origin_country = StringField(required=True)


class CarModel(BaseDocument):
    name = StringField(required=True)
    brand = ReferenceField(CarBrand)


class Car(BaseDocument):
    brand = ReferenceField(CarBrand)
    model = ReferenceField(CarModel)
    car_type = ReferenceField(CarType)
    color = StringField(required=True)
    year = IntField(required=True)
    millage = FloatField(required=True, min_value=0)
    license_plate = StringField(required=True)
    available = BooleanField(default=True)
    # photos = ListField(ImageField(size=(800, 600, True), thumbnail_size=(100, 75, True)))

    @classmethod
    async def createRecord(cls, car: NewCarParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            brandDoc = model.CarBrand.objects.get(id=car.brand)
            carTypeDoc = model.CarType.objects.get(id=car.car_type)
            modelDoc = model.CarModel.objects.get(id=car.model)
            car = dict(car)
            car['brand'] = brandDoc.id
            car['car_type'] = carTypeDoc.id
            car['model'] = modelDoc.id
            crud.create(car, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


class CarReservation(BaseDocument):
    user = ReferenceField(User)
    car = ReferenceField(Car)
    start = DateField(required=True)
    end = DateField(required=True)


class Reservation(BaseDocument):
    user = ReferenceField(User)
    hotel_reservation = ListField(ReferenceField(RoomReservation))
    car_reservation = ListField(ReferenceField(CarReservation))

