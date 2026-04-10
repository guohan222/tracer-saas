import datetime

from web import models

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count


def statistics(request, proj_id):
    return render(request, 'statistics.html')


# 饼图:优先级展示
def statistics_priority(request, proj_id):
    start = request.GET.get('start')
    end = request.GET.get('end')
    if end:
        end_date_obj = datetime.datetime.strptime(end, '%Y-%m-%d')
        end_date_obj += datetime.timedelta(days=1)
        end = end_date_obj.strftime('%Y-%m-%d')
    # 前端所需数据格式：[{name: '高', y: 10}, {name: '中', y: 5}]

    priority_dict = {}  # { key:{name:xx,y:xx}, }
    for key, value in models.Issues.priority_choices:
        priority_dict[key] = dict(name=value, y=0)

    # [{pri:xx,ct:xx},{}]
    result = models.Issues.objects.filter(project_id=proj_id, create_datetime__gte=start,
                                          create_datetime__lte=end).values('priority').annotate(
        ct=Count('id'))
    for item in result:
        priority_dict[item['priority']]['y'] = item['ct']

    priority_list = list(priority_dict.values())
    return JsonResponse({'status': True, 'priority_data': priority_list})


# 柱状图:人员工作进度
def statistics_user(request, proj_id):
    """
    前端所需数据&格式
    categories: ['武沛齐', '未指派']
    series: [{name: '新建', data: [1, 2]}, {name: '处理中', data: [0, 1]}]

    """

    # 得到包含所有成员名称的列表：categories
    creator = [request.tracer.project.creator.name]
    project_user_list = models.Participants.objects.filter(project_id=proj_id).values_list('user__name')
    participants = [item[0] for item in project_user_list]
    categories = creator + participants + ['未指派']


    # 构造全0矩阵，0待补位
    big_dict = {}  # { id:{ name:新建,data:[0,0,0,...(多少个人就多少个0)] }, }
    for key, value in models.Issues.status_choices:
        big_dict[key] = {'name':value,'data':[0 for i in range(len(categories))]}

    # 一次查库，双重分组
    # <QuerySet [{'assign__name': None, 'status': 3, 'ct': 1}, {'assign__name': None, 'status': 4, 'ct': 1}, {'assign__name': '郭晗', 'status': 1, 'ct': 1}, {'assign__name': '郭晗', 'status': 3, 'ct': 1}]>
    res = models.Issues.objects.filter(project_id=proj_id).values('assign__name', 'status').annotate(ct=Count('id'))

    # 填充big_dict中0这个待补位
    for item in res:
        target_dict = big_dict[item['status']]
        if item['assign__name'] is None:
            target_dict['data'][-1] = item['ct']
        else:
            index = categories.index(item['assign__name'])
            target_dict['data'][index] = item['ct']

    return JsonResponse({'status': True, 'categories': categories,'series':list(big_dict.values())})



























