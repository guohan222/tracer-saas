import datetime

from web import models

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count


def statistics(request, proj_id):
    return render(request, 'statistics.html')


# 饼图优先级展示
def statistics_priority(request, proj_id):
    start = request.GET.get('start')
    end = request.GET.get('end')
    if end:
        end_date_obj = datetime.datetime.strptime(end,'%Y-%m-%d')
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
