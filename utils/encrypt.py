import hashlib

from django.conf import settings

def md5(pwd):
    hashlib_obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hashlib_obj.update(pwd.encode('utf-8'))
    return hashlib_obj.hexdigest()
