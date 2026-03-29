from web import models

from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('inclusion/all_project.html')
def all_project_list(request):
    # 用户创建的项目
    my_proj_list = models.Project.objects.filter(creator=request.tracer.user)
    join_proj_list = models.Participants.objects.filter(user=request.tracer.user)
    return {'my_proj_list': my_proj_list, 'join_proj_list': join_proj_list}


@register.inclusion_tag('inclusion/manage_menu.html')
def manage_menu_list(request):
    proj_id = request.tracer.project.id
    menu_info = [
        {'title': '概 览', 'url': reverse('web:dashboard', kwargs={'proj_id': proj_id})},
        {'title': '问 题', 'url': reverse('web:issues', kwargs={'proj_id': proj_id})},
        {'title': '统 计', 'url': reverse('web:statistics', kwargs={'proj_id': proj_id})},
        {'title': '文 件', 'url': reverse('web:file', kwargs={'proj_id': proj_id})},
        {'title': 'wiki', 'url': reverse('web:wiki', kwargs={'proj_id': proj_id})},
        {'title': '设 置', 'url': reverse('web:settings', kwargs={'proj_id': proj_id})},
    ]

    for item in menu_info:
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'

    return {'menu_info': menu_info}
