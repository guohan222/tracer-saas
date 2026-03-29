app_name = 'web'

from django.contrib import admin
from django.urls import path,re_path
from web.views import account, project
from web.views import home

urlpatterns = [
    # path('admin/', admin.site.urls),

    # 未登录
    path('send/sms', account.send_sms, name='send_sms'),
    path('img/code/', account.img_code, name='img_code'),
    path('register/', account.register, name='register'),
    path('login/', account.login, name='login'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('index/', home.index, name='index'),

    # 登录后具有的权限
    path('logout/', account.logout, name='logout'),
    path('project/list/', project.project_list, name='project_list'),
    path('project/star/<str:proj_type>/<int:proj_id>', project.project_star, name='project_star'),
    path('project/unstar/<str:proj_type>/<int:proj_id>', project.project_unstar, name='project_unstar'),

]
