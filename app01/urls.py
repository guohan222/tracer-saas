from app01.views import register

app_name = 'app01'

from django.contrib import admin
from django.urls import path
from app01 import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('send/sms/', views.send_sms),
    path('register/', views.register,name='register'),
    path('account/', views.account,name='account'),
    path('project/create/', views.create_project,name='create_project'),
]