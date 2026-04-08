from django.core.signals import request_started
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm
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
            'form': form
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
def issues_detail(request, proj_id, issues_id):
    issues_obj = models.Issues.objects.filter(id=issues_id).first()

    def create_reply_record(content):
        # 创建一条操作评论
        reply_obj = models.IssuesReply.objects.create(
            reply_type=1,
            issues_id=issues_id,
            creator_id=request.tracer.user.id,
            content=content
        )
        # 给前端返回该评论进行挂载时需要的东西
        data_dict = {
            'id': reply_obj.id,
            'reply_type': reply_obj.get_reply_type_display(),
            'creator_name': reply_obj.creator.name,
            'content': reply_obj.content,
            'create_datetime': reply_obj.create_datetime,
            'parent_id': reply_obj.parent.id if reply_obj.parent else ''
        }
        return data_dict

    # 展示原有数据
    if request.method == "GET":
        form = IssuesModelForm(request, instance=issues_obj)
        return render(request, 'issues_detail.html', {'form': form, 'issues_obj': issues_obj})

    """
    普通文本字段：subject、desc、start_date、end_date
    choices字段：status、priority、mode
    页面FK字段：issues_type、module、assign、parent
    页面M2M字段：attention
    
    前端传来的数据格式：{field:xxx,value:xxx}
    """
    # 更新数据
    field = request.POST.get('field')
    value = request.POST.get('value')
    # 拿到该字段对象
    field_obj = models.Issues._meta.get_field(field)

    # 1. 普通文本字段
    if field in ['subject', 'desc', 'start_date', 'end_date']:
        # 判断值是否为空，为空则检查：是否允许为空
        if not value:
            if not field_obj.null:
                return JsonResponse({'status': False, 'errors': '值不能为空！'})
            # 否则允许为空，进行更新保存
            setattr(issues_obj, field, None)
            issues_obj.save(update_fields=[field, ])
            record_content = f'{field_obj.verbose_name}更新为空'
        else:
            print(value)
            setattr(issues_obj, field, value)
            issues_obj.save(update_fields=[field, ])
            record_content = f'更新了问题描述' if field == 'desc' else f'{field_obj.verbose_name}更新为:{value}'

        data = create_reply_record(record_content)

        return JsonResponse({'status': True, 'reply_obj': data})

    # 2. FK字段处理(FK字段时value为关联的对象的id)     issues_type、module、assign、parent
    if field in ['issues_type', 'module', 'parent', 'assign']:
        # 判断值是否为空，为空则检查：是否允许为空
        if not value:
            if not field_obj.null:
                return JsonResponse({'status': False, 'errors': '值不能为空！'})
            setattr(issues_obj, field, None)
            issues_obj.save(update_fields=[field])
            record_content = f'{field_obj.verbose_name}更新为空'

        else:  # 不为空则检测FK字段有没有其他要求，比如assign只能为该项目中的参与者或者创建者

            # 如果字段为assign,则要判断能否根据这个value找到属于该项目的人，如果不能则表明操作者通过手段，试图派给不属于该项目中的人
            if field == 'assign':
                # 检测是否派给了创建者
                if value == str(request.tracer.project.creator.id):
                    instance = request.tracer.project.creator
                else:  # 否则是派给了参与者，则需检测能否根据这个value(此时为id)在这个项目中找到具体的人
                    participants_obj = models.Participants.objects.filter(project_id=proj_id, user_id=value).first()
                    if participants_obj:
                        instance = participants_obj.user
                    else:  # 用户通过手段，试图派给不属于该项目中的人
                        return JsonResponse({'status': False, 'errors': '选择的值不存在'})

                # 上面通过则代表操作者正常执行，assign字段待更新的值的合法的
                setattr(issues_obj, field, instance)
                issues_obj.save(update_fields=[field])
                record_content = f'{field_obj.verbose_name}更新为:{str(instance)}'

            else:  # 检测其他FK字段根据value查找，是否真实存在且合法
                """
                    外键字段.remote_field——》找到这个外键字段关联哪张表
                    外键字段.remote_field.model——》这个外键字段关联的那张表的model类
                """
                instance = field_obj.remote_field.model.objects.filter(id=value, project_id=proj_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'errors': '选择的值不存在'})
                setattr(issues_obj, field, instance)
                issues_obj.save(update_fields=[field])
                record_content = f'{field_obj.verbose_name}更新为:{str(instance)}'

        data = create_reply_record(record_content)
        return JsonResponse({'status': True, 'reply_obj': data})


    # 3. choices字段处理       status、priority、mode
    if field in ['priority', 'status', 'mode']:
        select_text = None
        for key,text in field_obj.choices:
            if str(key) == value:
                select_text = text
        if not select_text:
            return JsonResponse({'status': False, 'errors': '选择的值不存在'})
        setattr(issues_obj,field,value)
        issues_obj.save(update_fields=[field])
        record_content = f'{field_obj.verbose_name}更新为:{select_text}'
        data = create_reply_record(record_content)
        return JsonResponse({'status': True, 'reply_obj': data})

    # 4. M2M字段      attention
    if field == 'attention':
        # {field:xxx,value:[id,id,xx]}
        value = request.POST.getlist('value')
        print(type(value))
        print(f'm2m：{value}')
        if not isinstance(value,list):
            return JsonResponse({'status':False,'error':'数据格式错误'})
        if not value:
            issues_obj.attention.set(value)
            record_content = f'{field_obj.verbose_name}更新为空'
        else:   # 关注者同assign一样必须是属于该项目的人
            user_dict = {str(request.tracer.project.creator.id):request.tracer.project.creator.name}
            participants_list = models.Participants.objects.filter(project_id=proj_id)
            for item in participants_list:
                user_dict[str(item.user.id)] = item.user.name

            new_attention_name = []
            for user_id in value:
                user_name = user_dict.get(str(user_id),'')
                if not user_name:
                    # 必须全部都合理
                    return JsonResponse({'status': False, 'errors': '选择的值不存在'})
                new_attention_name.append(user_name)

            issues_obj.attention.set(value)
            record_content = f'{field_obj.verbose_name}更新为:{new_attention_name}'
        data = create_reply_record(record_content)
        return JsonResponse({'status': True, 'reply_obj': data})

    return HttpResponse('sb')


# 展示&新建评论
@csrf_exempt
def issues_record(request, proj_id, issues_id):
    if request.method == "GET":
        # 按时间正序排,防止子评论早出现找不到父评论
        reply_objs = models.IssuesReply.objects.filter(issues_id=issues_id).order_by('create_datetime')
        reply_obj_list = []
        for row in reply_objs:
            data = {
                'id': row.id,
                'reply_type': row.get_reply_type_display(),
                'creator_name': row.creator.name,
                'content': row.content,
                'create_datetime': row.create_datetime,
                'parent_id': row.parent.id if row.parent else ''
            }
            reply_obj_list.append(data)
        return JsonResponse({'status': True, 'reply_obj_list': reply_obj_list})

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
        return JsonResponse({'status': True, 'reply_obj': data})
    return JsonResponse({'status': False, 'errors': form.errors.get_json_data()})
