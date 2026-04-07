
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from web import models
from web.forms.issues import IssuesModelForm,IssuesReplyModelForm
from utils.pagination import Pagination



# 展示&新建问题
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


# 编辑问题
@csrf_exempt
def issues_detail(request,proj_id,issues_id):
    issues_obj = models.Issues.objects.filter(id=issues_id).first()

    # 展示原有数据
    if request.method == "GET":
        form = IssuesModelForm(request,instance=issues_obj)
        return render(request,'issues_detail.html',{'form':form,'issues_obj':issues_obj})

    # 更新数据
    """
    普通文本字段：subject、desc、start_date、end_date
    choices字段：status、priority、mode
    页面FK字段：issues_type、module、assign、parent
    页面M2M字段：attention
    
    前端传来的数据格式：{field:xxx,value:xxx}
    """
    field = request.POST.get('field')
    value = request.POST.get('value')
    # 拿到该字段对象
    field_obj = models.Issues._meta.get_field(field)

    # 1. 普通文本字段
    if str(field) in ['subject','desc','start_date','end_date']:
        # 判断值是否为空，为空则检查：是否允许为空
        if not value:
            if not field_obj.null:
                return JsonResponse({'status':False,'errors':'值不能为空！'})
            # 否则允许为空，进行更新保存
            setattr(issues_obj,field,None)
            issues_obj.save(update_fields=[field,])
            record_content = f'{field_obj.verbose_name}更新为:{value}'
        else:
            setattr(issues_obj, field, value)
            issues_obj.save(update_fields=[field, ])
            record_content = f'{field_obj.verbose_name}更新为:{value}'

        # 创建一条操作评论
        reply_obj = models.IssuesReply.objects.create(
            reply_type = 1,
            issues_id = issues_id,
            creator_id = request.tracer.user.id,
            content = record_content
        )
        # 给前端返回该评论进行挂载时需要的东西
        data = {
            'id': reply_obj.id,
            'reply_type': reply_obj.get_reply_type_display(),
            'creator_name': reply_obj.creator.name,
            'content': reply_obj.content,
            'create_datetime': reply_obj.create_datetime,
            'parent_id': reply_obj.parent.id if reply_obj.parent else ''
        }
        return JsonResponse({'status':True,'reply_obj':data})

    return HttpResponse('sb')





















# 展示&新建评论
@csrf_exempt
def issues_record(request,proj_id,issues_id):
    if request.method == "GET":
        # 按时间正序排,防止子评论早出现找不到父评论
        reply_objs = models.IssuesReply.objects.filter(issues_id=issues_id).order_by('create_datetime')
        reply_obj_list = []
        for row in reply_objs:
            data = {
                'id':row.id,
                'reply_type':row.get_reply_type_display(),
                'creator_name':row.creator.name,
                'content':row.content,
                'create_datetime':row.create_datetime,
                'parent_id':row.parent.id if row.parent else ''
            }
            reply_obj_list.append(data)
        return JsonResponse({'status':True,'reply_obj_list':reply_obj_list})

    # 新建评论
    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.reply_type = 2
        form.instance.issues_id = issues_id
        form.instance.creator_id = request.tracer.user.id
        reply_obj = form.save()
        data = {
            'id': reply_obj.id,
            'reply_type': reply_obj.get_reply_type_display(),
            'creator_name': reply_obj.creator.name,
            'content': reply_obj.content,
            'create_datetime': reply_obj.create_datetime,
            'parent_id': reply_obj.parent.id if reply_obj.parent else ''
        }
        return JsonResponse({'status':True,'reply_obj':data})
    return JsonResponse({'status':False,'errors':form.errors.get_json_data()})



