from web import models

from django.shortcuts import render
from django.db.models.aggregates import Count

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
    issues_updates = models.IssuesReply.objects.filter(reply_type=1).select_related('issues','creator')[0:7]


    content = {
        'issues_dict': issues_dict,
        'total_user': total_user,
        'issues_updates': issues_updates,
    }
    return render(request, 'dashboard.html', content)
