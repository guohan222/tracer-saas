import datetime
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.shortcuts import redirect

from web import models
from django.utils.deprecation import MiddlewareMixin

class Tracer:
    def __init__(self):
        self.user = None
        self.product = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        request.tracer = Tracer()

        # 获取用户是否已登录信息
        user_id = request.session.get('user_id',0)
        user_obj = models.User.objects.filter(id=user_id).first()

        request.tracer.user = user_obj


        # 判断请求地址需否需要具有登录权限
        if request.path_info in settings.URL_WHITE_LIST:
            return None
        if not request.tracer.user:
            return redirect('web:login')


        # 如果用户登录了,则获取用户目前订阅信息
        subscribe_obj = models.Subscribe.objects.filter(user=user_obj,status=2).order_by('-pk').first()
        current_time = datetime.datetime.now()
        if subscribe_obj.end_time and subscribe_obj.end_time < current_time:
            subscribe_obj = models.Subscribe.objects.filter(user=user_obj, status=2).order_by('pk').first()
        user_product = subscribe_obj.product if user_obj else None

        request.tracer.product =  user_product

        return None

    def process_view(self,request,view_func,view_args,view_kwargs):
        project_id = view_kwargs.get('proj_id')

        # 判断url是否以manage开头，若不是则不用进行判断项目与用户有没有关系
        if not request.path_info.startswith('/manage/'):
            return None

        # 如果不是则判断项目和用户有没有关系
        project_obj = models.Project.objects.filter(creator=request.tracer.user,id=project_id).first()
        if project_obj:
            # 如果是我创建的则让其通过
            request.tracer.project =project_obj
            return None
        participants_obj = models.Participants.objects.filter(user=request.tracer.user,id=project_id).first()
        if participants_obj:
            # 如果是我参加的
            request.tracer.project = participants_obj.project
            return None

        # 项目和我无关不允通过
        return redirect('web:project_list')
