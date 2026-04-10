import datetime

from django.http import JsonResponse

from web import models

from django.shortcuts import render
from django.db.models.aggregates import Count
from django.db.models.functions import TruncDate

from web.views.issues import issues


# 概览
def dashboard(request, proj_id):
    # 问题status的处理
    issues_dict = {}  # { id:{text:新建,} , }
    # <QuerySet [{'status': 1, 'ct': 2}, {'status': 7, 'ct': 1}]>
    issues_group = models.Issues.objects.filter(project_id=proj_id).values('status').annotate(ct=Count('id'))
    status_choices = models.Issues.status_choices

    for key, value in status_choices:
        issues_dict[key] = {'text': value, 'ct': 0}
    for item in issues_group:
        issues_dict[item['status']]['ct'] = item['ct']

    # 项目成员
    total_user = [(request.tracer.project.creator.id, request.tracer.project.creator.name), ]
    join_user = models.Participants.objects.filter(project_id=proj_id).values_list('user_id', 'user__name')
    total_user.extend(join_user)

    # 问题变更动态

    # issues_updates = models.Issues.objects.filter(
    #     project_id=proj_id,
    #     assign__isnull=False
    # ).select_related(
    #     'assign','creator'
    # ).prefetch_related(
    #     'attention'
    # ).order_by('-latest_update_datetime')[0:5]
    issues_updates = models.IssuesReply.objects.filter(reply_type=1, project_id=proj_id).select_related('issues',
                                                                                                        'creator').order_by(
        '-create_datetime')[0:7]

    content = {
        'issues_dict': issues_dict,
        'total_user': total_user,
        'issues_updates': issues_updates,
    }
    return render(request, 'dashboard.html', content)


# issues_chart
def issues_chart(request, proj_id):
    # x轴（时间）,当前以及前30天
    today = datetime.datetime.now().date()
    date_dict = {}
    for i in range(30):
        # 字典（有序）：从30天前->今天
        date = today - datetime.timedelta(days=29-i)
        # 暂时默认每天的问题数为0
        date_dict[date.strftime('%Y-%m-%d')] = 0

    # 查询时间大于前三十天的,所有问题数据,以日期分组
        # 对应SQL语句：'select 时间格式化到日期 as ctime, ct from Issues where ...  group_by ctime'
    result = models.Issues.objects.filter(project_id=proj_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).annotate(
        ctime=TruncDate('create_datetime')).values('ctime').annotate(ct=Count('id'))

    for item in result:
        date_str = item['ctime'].strftime('%Y-%m-%d')
        date_dict[date_str] = item['ct']

    return JsonResponse({'status':True,'date':list(date_dict.keys()),'count':list(date_dict.values())})