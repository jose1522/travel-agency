import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from settings import settings


class EncryptedString(str):
    def __init__(self, text: str):
        super().__init__()
        self.text = text


class HashedString(str):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

class Cipher:
    def __init__(self):
        # self.__salt = os.urandom(16)
        # self.__kdf = PBKDF2HMAC(
        #     algorithm=hashes.SHA256(),
        #     length=32,
        #     salt=self.__salt,
        #     iterations=100000,
        #     backend=default_backend()
        # )
        # self.__key = base64.urlsafe_b64encode(self.__kdf.derive(settings.DB_ENCRYPTION_KEY.encode('utf8')))
        # self.__f = Fernet(self.__key)
        self.__f = Fernet(settings.DB_ENCRYPTION_KEY.encode('utf8'))

    @classmethod
    def encryptString(cls, value: str) -> str:
        e = cls()
        value = e.__f.encrypt(bytes(value, encoding="utf8"))
        return value.decode('utf8')

    @classmethod
    def decryptString(cls, value: str) -> EncryptedString:
        e = cls()
        value = e.__f.decrypt(bytes(value.encode('utf8')))
        value = EncryptedString(value.decode('utf8'))
        return value