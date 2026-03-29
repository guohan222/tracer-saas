app_name = 'web'

from django.contrib import admin
from django.urls import path
from web.views import account, project, home, manage

urlpatterns = [
    # path('admin/', admin.site.urls),

    # 未登录
    path('send/sms', account.send_sms, name='send_sms'),
    path('img/code/', account.img_code, name='img_code'),
    path('register/', account.register, name='register'),
    path('login/', account.login, name='login'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('index/', home.index, name='index'),

    # 管理项目列表
    path('logout/', account.logout, name='logout'),
    path('project/list/', project.project_list, name='project_list'),
    path('project/star/<str:proj_type>/<int:proj_id>/', project.project_star, name='project_star'),
    path('project/unstar/<str:proj_type>/<int:proj_id>/', project.project_unstar, name='project_unstar'),

    # 进入项目
    path('manage/<int:proj_id>/', ([
                                      path('dashboard/', manage.dashboard, name='dashboard'),
                                      path('issues/', manage.issues, name='issues'),
                                      path('statistics/', manage.statistics, name='statistics'),
                                      path('file/', manage.file, name='file'),
                                      path('wiki/', manage.wiki, name='wiki'),
                                      path('settings/', manage.settings, name='settings'),

                                  ], None, None)),



]
