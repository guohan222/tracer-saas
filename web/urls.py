app_name = 'web'

from django.contrib import admin
from django.urls import path
from web.views import account
urlpatterns = [
    path('admin/', admin.site.urls),
    path('send/sms', account.send_sms,name='send_sms'),
    path('register/', account.register,name='register'),
]