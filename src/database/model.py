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
from database import RoomNotAvailableError
import json


class User(BaseDocument):
    username = StringField(max_length=120, required=True, unique=True)
    password = StringField(max_length=120, required=True)
    isAdmin = BooleanField(default=True)

    meta = {
        'indexes': ['username'],
        'exclude_from_update': ['isAdmin', 'active', 'createdOn', 'deletedOn']
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
    async def updateRecord(cls, currentUser, newData: dict):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            if "password" in newData:
                newData['password'] = get_hash(newData['password'])
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
            await UserInfo.deleteRecord(crud.documents[0].id)
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
    identification = EncryptedStringField(min_length=5, max_length=25)
    first_name = EncryptedStringField(required=True, max_length=50, min_length=3)
    last_name = EncryptedStringField(required=True, max_length=50, min_length=3)
    second_last_name = EncryptedStringField(max_length=50, min_length=3)
    email = EmailField(required=True, unique=True, min_length=5, max_length=100)
    birthday = DateField(default=datetime.today())
    phone = StringField(min_length=5, max_length=20)

    meta = {
        'indexes': ['user_id'],
        'exclude_from_update': ['user_id', 'id', 'active', 'createdOn', 'deletedOn']
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
            if data is None:
                raise DoesNotExist
            else:
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
    email = EmailField(required=True, unique=True, min_length=5, max_length=50)
    address = StringField(required=True, max_length=200, min_length=2)
    point = PointField(default=[0,0])
    phone = StringField(required=True, min_length=5, max_length=15)
    rating = IntField(required=True, max_value=5)

    meta = {
        'indexes': ['$name', 'rating', 'active', 'createdOn', 'deletedOn']
    }


class RoomType(BaseDocument):
    name = StringField(required=True, unique_with=['hotel'])
    hotel = ReferenceField(Hotel)
    amenities = ListField()
    price = FloatField(required=True)
    capacity = IntField(default=2, min_value=1, max_value=10)
    description = StringField()

    meta = {
        'exclude_from_update': ['hotel', 'id', 'active', 'createdOn', 'deletedOn']
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
            msg.addMessage('Error', str(e))
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

    meta = {
        'exclude_from_update': ['hotel', 'room_type', 'id', 'active', 'createdOn', 'deletedOn']
    }

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
        except NotUniqueError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            return msg.data
        else:
            return msg.data


class RoomReservation(BaseDocument):
    user = ReferenceField(User)
    room = ReferenceField(Room)
    start = DateField(required=True)
    end = DateField(required=True)

    meta = {
        'exclude_from_update': ['room', 'active', 'user', 'createdOn', 'deletedOn']
    }

    @classmethod
    async def createRecord(cls, room: NewRoomReservationParams, userDoc: User):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            roomDoc = model.Room.objects.get(id=room.room)
            if not roomDoc.available:
                raise RoomNotAvailableError
            else:
                roomDoc.update(available=False)
            room = dict(room)
            room['room'] = roomDoc.id
            room['user'] = userDoc['id']
            crud.create(room, msg)
            return msg.data
        except RoomNotAvailableError:
            raise
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except NotUniqueError as e:
            logging.error(str(e))
            msg.addMessage('Error', str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def deleteRecord(cls, objectID: str) -> None:
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"id": objectID, 'active': True}
            crud.read(query=query)
            crud.delete(msg)
            roomDoc = Room.objects.get(id=crud.documents[0].room.id)
            roomDoc.update(available=True)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            raise e


class CarType(BaseDocument):
    name = StringField(required=True, unique=True)
    drive = StringField(required=True, choices=('4WD', '2WD', 'AWD'), unique_with=["category", "engine"])
    category = StringField(required=True, choices=('Hatchback', 'Sedan', 'SUV', 'Compact'))
    engine = StringField(required=True, choices=('Electric', 'Diesel', 'Gasoline'))
    capacity = IntField(default=5)

    meta = {
        'exclude_from_update': ['active', 'createdOn', 'deletedOn']
    }


class CarBrand(BaseDocument):
    name = StringField(required=True)
    origin_country = StringField(required=True)
    meta = {
        'exclude_from_update': ['active', 'createdOn', 'deletedOn']
    }


class CarModel(BaseDocument):
    name = StringField(required=True, unique_with=['brand'])
    brand = ReferenceField(CarBrand)
    price = FloatField(max_value=0)
    meta = {
        'exclude_from_update': ['brand', 'active', 'createdOn', 'deletedOn']
    }

    @classmethod
    async def createRecord(cls, model: NewCarModelParams):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            carBrand = CarBrand.objects.get(id=model.brand)
            model = dict(model)
            model['brand'] = carBrand.id
            crud.create(model, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except NotUniqueError as e:
            logging.error(str(e))
            msg.addMessage('Error', str(e))
            raise
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


class Car(BaseDocument):
    brand = ReferenceField(CarBrand)
    model = ReferenceField(CarModel)
    car_type = ReferenceField(CarType)
    color = StringField(required=True)
    year = IntField(required=True)
    millage = FloatField(required=True, min_value=0)
    license_plate = StringField(required=True, unique=True)
    available = BooleanField(default=True)
    # photos = ListField(ImageField(size=(800, 600, True), thumbnail_size=(100, 75, True)))

    meta = {
        'exclude_from_update': ['brand', 'model', 'car_type', 'active', 'createdOn', 'deletedOn']
    }

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

    meta = {
        'exclude_from_update': ['user', 'car', 'active', 'createdOn', 'deletedOn']
    }
    @classmethod
    async def createRecord(cls, reservation: NewCarReservationParams, user: dict):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            userDoc = model.User.objects.get(id=user['id'])
            carDoc = model.Car.objects.get(id=reservation.car)
            reservation = dict(reservation)
            reservation['user'] = userDoc.id
            reservation['car'] = carDoc.id
            crud.create(reservation, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise


class Reservation(BaseDocument):
    user = ReferenceField(User)
    hotel_reservation = ListField(ReferenceField(RoomReservation))
    car_reservation = ListField(ReferenceField(CarReservation))
    total = FloatField(min_value=1)
    paid = BooleanField(default=False)
    meta = {
        'exclude_from_update': ['user', 'hotel_reservation', 'car_reservation', 'active', 'createdOn', 'deletedOn']
    }

    @classmethod
    async def createRecord(cls, reservation: NewReservationParams, user: dict):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            hotelDoc = model.RoomReservation.query(
                query={"id__in": reservation.hotel_reservation, "user": user["id"], 'active': True},
            )
            carDoc = model.CarReservation.query(
                query={"id__in": reservation.car_reservation, "user": user["id"], 'active': True},
            )
            userDoc = model.User.objects.get(id=user['id'])
            reservation = dict(reservation)
            reservation['user'] = userDoc.id
            if isinstance(hotelDoc, list):
                reservation['hotel_reservation'] = list(map(lambda x: x.id, hotelDoc))
            else:
                reservation['hotel_reservation'] = [hotelDoc.id]
            if isinstance(carDoc, list):
                reservation['car_reservation'] = list(map(lambda x: x.id, carDoc))
            else:
                reservation['car_reservation'] = [carDoc.id]
            crud.create(reservation, msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise
