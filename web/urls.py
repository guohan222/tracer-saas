app_name = 'web'

from django.contrib import admin
from django.urls import path
from web.views import account, project, home, statistics, wiki, file, settings, issues,dashboard

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
                                       path('dashboard/', dashboard.dashboard, name='dashboard'),
                                       path('dashboard/issues/chart/', dashboard.issues_chart, name='issues_chart'),

                                       # issues
                                       path('issues/', issues.issues, name='issues'),
                                       path('issues/detail/<int:issues_id>/', issues.issues_detail, name='issues_detail'),
                                       path('issues/record/<int:issues_id>/', issues.issues_record, name='issues_record'),
                                       path('issues/invite/url/', issues.invite_url, name='invite_url'),

                                       path('statistics/', statistics.statistics, name='statistics'),

                                       # file
                                       path('file/', file.file, name='file'),
                                       path('file/del/', file.file_del, name='file_del'),
                                       path('upload/credential/', file.upload_credential, name='upload_credential'),
                                       path('file/add/', file.file_add, name='file_add'),
                                       path('file/download/<int:file_id>', file.file_download, name='file_download'),

                                       # wiki
                                       path('wiki/', wiki.wiki, name='wiki'),
                                       path('wiki/add/', wiki.wiki_add, name='wiki_add'),
                                       path('wiki/del/', wiki.wiki_del, name='wiki_del'),
                                       path('wiki/edit/', wiki.wiki_edit, name='wiki_edit'),
                                       path('wiki/upload/', wiki.wiki_upload, name='wiki_upload'),

                                       # setting
                                       path('settings/', settings.settings, name='settings'),
                                       path('settings/del/', settings.settings_del, name='settings_del'),

                                   ], None, None)),

path('invite/join/<str:code>', issues.invite_join, name='invite_join'),

]
