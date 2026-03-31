import hashlib
import uuid

from django.conf import settings

def md5(pwd):
    hashlib_obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hashlib_obj.update(pwd.encode('utf-8'))
    return hashlib_obj.hexdigest()


# cos中避免文件名重复
def uid(string):
    data = f'{uuid.uuid4()}-{string}'
    return md5(data)