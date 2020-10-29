from mongoengine import connect
from settings import settings


class RoomNotAvailableError(Exception):
    def __init__(self, message="Room is not available"):
        self.message = message
        super().__init__(self.message)


connect(
    db=settings.MONGO_DB,
    # authentication_source=settings.MONGO_AUTH_SOURCE,
    # username=settings.MONGO_USER,
    # password=settings.MONGO_SECRET,
    host=settings.MONGO_HOST
)



