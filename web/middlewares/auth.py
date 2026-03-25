from django.utils.deprecation import MiddlewareMixin
from web import models

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get('user_id',0)
        user_obj = models.User.objects.filter(id=user_id).first()
        request.tracer = user_obj

