from __future__ import absolute_import
from core.security.sanitizer import Sanitizer
from core.security.authentication import get_hash
from core.security.encryption import Cipher, EncryptedString, HashedString
from mongoengine import StringField, BooleanField, Document, DateField, QuerySet, queryset_manager, DateTimeField, MultipleObjectsReturned, DoesNotExist, ValidationError, NotUniqueError
import mongoengine_goodjson as gj
from database.controller import CRUD
from api.messages import Message
from datetime import datetime
import logging
import json


class SanitizedStringField(StringField):
    def to_mongo(self, value):
        if value:
            value = Sanitizer.sanitize(value)
        # value = super(SanitizedStringField, self).to_mongo(value)
        return value


class PasswordStringField(StringField):
    def to_mongo(self, value):
        if value and not isinstance(value, HashedString):
            value = get_hash(value)
        return value

    def to_python(self, value):
        if value:
            value = HashedString(value)
        return value


class EncryptedStringField(StringField):
    def to_mongo(self, value):
        if value and not isinstance(value, EncryptedString):
            value = Cipher.encryptString(value)
        return value

    def to_python(self, value):
        if value:
            try:
                value = Cipher.decryptString(value)
            except:
                pass
        return value


class BaseDocument(gj.Document):
    active = BooleanField(default=True)
    createdOn = DateField(default=datetime.today())
    deletedOn = DateField()

    meta = {
        'abstract': True
    }

    @classmethod
    async def createRecord(cls, **kwargs):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            crud.create(kwargs, msg)
        except NotUniqueError as e:
            logging.error(str(e))
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @classmethod
    async def searchWithParams(cls, skip, limit, expand: list = None, **kwargs) -> dict:
        crud = CRUD(cls=cls)
        try:
            kwargs["active"] = True
            crud.read(query=kwargs, skip=skip, limit=limit, exclude=['createdOn', 'active'])
            data = crud.toJSON(expand)
            return data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            logging.error(str(e))
            raise

    @classmethod
    async def deleteRecord(cls, objectID: str) -> None:
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"id": objectID, 'active': True}
            crud.read(query=query)
            crud.delete(msg)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            raise e

    @classmethod
    async def updateRecord(cls, **kwargs):
        msg = Message()
        crud = CRUD(cls=cls)
        try:
            query = {"id": kwargs.get('id'), 'active': True}
            exclude = cls._meta.get("exclude_from_update", [])
            if 'id' not in exclude:
                exclude.append('id')
            crud.read(query=query)
            crud.update(kwargs, msg, exclude=exclude)
            return msg.data
        except DoesNotExist:
            raise
        except ValidationError as e:
            logging.error(str(e))
            raise ValidationError
        except Exception as e:
            msg.addMessage('Error', str(e))
            raise

    @queryset_manager
    def query(self,
              queryset,
              query: dict,
              sortParams: list = None,
              limit: int = None,
              skip: int = None,
              exclude: list = None,
              only: list = None,
              ):

        data = queryset.filter(**query)

        if exclude is not None:
            data = data.exclude(*exclude)

        if skip is not None:
            data = data.skip(skip)

        if limit is not None:
            data = data.limit(limit)

        if sortParams is not None:
            data = data.order_by(*sortParams)

        if only is not None:
            data = data.only(*only)

        try:
            data = data.get()
        except MultipleObjectsReturned:
            data = list(data)
        except DoesNotExist:
            logging.error("Query {0} returned no results".format(query))
            data = None
        except ValidationError as e:
            logging.error("Query {0} had an error {1}".format(query,str(e)))
            data = None
        except Exception as e:
            logging.error("Query {0} had an error: {1}".format(query, str(e)))
        finally:
            return data

    def to_dict(self, expand: list = None):
        result = json.loads(self.to_json())
        if expand is not None:
            for item in expand:
                if item in self:
                    obj = getattr(self, item)
                    result[item] = json.loads(obj.to_json())
        return result