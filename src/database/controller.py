import json
from pydantic import BaseModel
from api.messages import Message
from datetime import datetime
from mongoengine import DoesNotExist


class CRUD:

    def __init__(self, cls):
        self.cls = cls
        self.documents = None

    def toJSON(self, expand: list = None):
        if self.documents is not None:
            if isinstance(self.documents, list):
                myArr = []
                for doc in self.documents:
                    myArr.append(doc.to_dict(expand=expand))
                return myArr
            else:
                return self.documents.to_dict(expand=expand)
        else:
            return None

    def create(self, data: dict, msg: Message) -> None:
        self.documents = self.cls(**data)
        self.documents.save()
        msg.addMessage('Created', self.toJSON())

    def update(self, data: BaseModel, msg: Message, cascade: bool = None, exclude: list = []) -> None:
        data = dict(data)
        if self.documents is not None:
            for doc in self.documents:
                for key, value in data.items():
                    if key not in exclude:
                        doc.__setattr__(key, value)
                if cascade is not None:
                    doc.save(cascade=cascade)
                else:
                    doc.save()
            msg.addMessage('Updated', self.toJSON())

    def delete(self, msg: Message, cascade: bool = False, softDelete: bool = True) -> None:
        if self.documents is not None:
            ids = []
            for doc in self.documents:
                ids.append(str(doc.id))
                if softDelete:
                    doc.__setattr__('active', False)
                    doc.__setattr__('deletedOn', datetime.today())
                else:
                    doc.delete()
                    if cascade:
                        doc.save(cascade=cascade)
                doc.save()
            msg.addMessage("Deleted", ids)

    def read(self,
             query: dict,
             sortParams: list = None,
             limit: int = None,
             skip: int = None,
             exclude: list = None,
             only: list = None) -> None:

        result = self.cls.query(query=query,
                                sortParams=sortParams,
                                limit=limit,
                                skip=skip,
                                exclude=exclude,
                                only=only)
        if result is None:
            raise DoesNotExist

        if not isinstance(result, list):
            result = [result]
        self.documents = result
