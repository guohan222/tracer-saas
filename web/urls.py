app_name = 'web'

from django.contrib import admin
from django.urls import path
from web.views import account
from web.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('send/sms', account.send_sms, name='send_sms'),
    path('img/code/', account.img_code, name='img_code'),
    path('register/', account.register, name='register'),
    path('login/', account.login, name='login'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('index/', home.index, name='index'),

]
