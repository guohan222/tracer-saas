from django.shortcuts import render
from django.http import JsonResponse

from web import models
from web.forms.issues import IssuesModelForm
from utils.pagination import Pagination



# 展示&新建
def issues(request, proj_id):
    if request.method == "GET":
        print(f'get请求:{request.GET}')
        form = IssuesModelForm(request)
        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=proj_id)
        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET
        )
        issues_obj_list = queryset[page_obj.start:page_obj.end]

        content = {
            'issues_object_list': issues_obj_list,
            'page_html': page_obj.page_html(),
            'form':form
        }
        return render(request, 'issues.html', content)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        # exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        form.instance.project_id = proj_id
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors.get_json_data()})


# 编辑
def issues_detail(request,proj_id,issues_id):
    issues_obj = models.Issues.objects.filter(id=issues_id).first()

    if request.method == "GET":
        form = IssuesModelForm(request,instance=issues_obj)
        return render(request,'issues_detail.html',{'form':form,'issues_obj':issues_obj})

    form = IssuesModelForm(request, data=request.POST,instance=issues_obj)
    if form.is_valid():
        # exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        form.instance.project_id = proj_id
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors.get_json_data()})
