import datetime
from datetime import timedelta
from itertools import product

from django.urls import reverse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from utils.encrypt import uid
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, ProjectInviteModelForm
from utils.pagination import Pagination


class CheckFilter(object):
    """
        自定义生成器组件，构造筛选按钮（核心url的构建）
    1. 字段名，用于构建查询参数字段
    2. 数据源，将哪些数据构建为按钮
    3. request,用于查询当前查询参数，判断按钮是否进行高亮、预测url

    """

    def __init__(self, field, data_list, request):
        self.field = field
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        # 将字段可以选择的值：生成筛选按钮，并预测未来点击该按钮时，url中该字段的查询是否要携带这个值
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ''

            # 目前该字段在url中的值
            # 后面利用这个变量来设置，点击这个值对应的按钮时，该字段查询的参数
            value_list = self.request.GET.getlist(self.field)

            # 如果循环到的这个choices的值在查询参数中，则对这个值的按钮进行高亮
            if key in value_list:
                # 进行高亮
                ck = 'checked'
                # 当前这个值在url里面了，所以这个值生成的按钮下次点击时肯定是取消这个筛选，
                # 所以要在value_list剔除这个key,确保如果真点击了这个按钮后，该值不在里面即不再url中
                value_list.remove(key)
            else:
                # 不在则表明，下次点击这按钮时，代表要用这个条件查询，则加入value_list
                value_list.append(key)

            # 进行生成：该值对应的按钮未来点击时，url中的参数是什么（有还是没有这个key，在上面value_list中表明了答案）
            query_dict = self.request.GET.copy()
            # 允许copy的request.GET可以进行更改
            query_dict._mutable = True
            # request.GET获取的查询参数中，只改变该字段，其他字段不受影响       eg：{name:1,age:2} ————》{name:2,age:2}
            query_dict.setlist(self.field, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            # 将变更的request.GET变成url中查询参数形式                      eg：?字段1=值1&字段1=值2&字段2=值1形式
            params_url = query_dict.urlencode()
            if params_url:
                url = f'{self.request.path_info}?{params_url}'
            else:
                url = f'{self.request.path_info}'
            tpl = f'<a class="cell" href="{url}"><input type="checkbox" {ck} /> {text}</a>'

            yield mark_safe(tpl)


class SelectFilter(object):
    def __init__(self, field, data_list, request):
        self.field = field
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            st = ''
            value_list = self.request.GET.getlist(self.field)
            if key in value_list:
                st = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.field, value_list)

            if 'page' in query_dict:
                query_dict.pop('page')
            param_url = query_dict.urlencode()
            if param_url:
                url = f'{self.request.path_info}?{param_url}'
            else:
                url = f'{self.request.path_info}'

            tpl = f'<option value={url} {st}>{text}</option>'
            yield mark_safe(tpl)


# 展示&新建问题
def issues(request, proj_id):
    # 如果用户进行筛选，url查询参数示例：?issues_type=1&status=2&status=3（同字段或，不同字段且）
    if request.method == "GET":
        # 首先定一个允许的查询字段列表，然后循环这个列表看url中有没有查询参数字段在这个列表中如果有则以这个字段名__in为键，getlist到的值为值，存储到condition字典里面
        print(f'issues中get请求:{request.GET}')
        # 允许进行筛选的字段
        allowed_fields = ['issues_type', 'priority', 'status', 'assign', 'attention']
        condition = {}
        for item in allowed_fields:
            # 检测用户url中查询参数是否在其中
            if not request.GET.get(item):
                continue
            # 如果有将查询参数记录下
            condition[f'{item}__in'] = request.GET.getlist(item)

        form = IssuesModelForm(request)
        invite_form = ProjectInviteModelForm()
        # 根据查询条件,分页获取数据
        queryset = models.Issues.objects.filter(project_id=proj_id, **condition)
        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET
        )
        issues_obj_list = queryset[page_obj.start:page_obj.end]

        issues_type_list = models.IssuesType.objects.filter(project_id=proj_id).values_list('id', 'title')
        proj_user_list = [(request.tracer.project.creator.id, request.tracer.project.creator.name), ]
        proj_user_list.extend(
            models.Participants.objects.filter(project_id=proj_id).values_list('user_id', 'user__name'))

        content = {
            'issues_object_list': issues_obj_list,
            'page_html': page_obj.page_html(),
            'filter_list': [
                {'title': '状态', 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': '优先级', 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': '问题类型', 'filter': CheckFilter('issues_type', issues_type_list, request)},
                {'title': '指派', 'filter': SelectFilter('assign', proj_user_list, request), 'class_type': 'select'},
                {'title': '关注者', 'filter': SelectFilter('attention', proj_user_list, request),
                 'class_type': 'select'},
            ],
            'form': form,
            'invite_form':invite_form
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
        for key, text in field_obj.choices:
            if str(key) == value:
                select_text = text
        if not select_text:
            return JsonResponse({'status': False, 'errors': '选择的值不存在'})
        setattr(issues_obj, field, value)
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
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': '数据格式错误'})
        if not value:
            issues_obj.attention.set(value)
            record_content = f'{field_obj.verbose_name}更新为空'
        else:  # 关注者同assign一样必须是属于该项目的人
            user_dict = {str(request.tracer.project.creator.id): request.tracer.project.creator.name}
            participants_list = models.Participants.objects.filter(project_id=proj_id)
            for item in participants_list:
                user_dict[str(item.user.id)] = item.user.name

            new_attention_name = []
            for user_id in value:
                user_name = user_dict.get(str(user_id), '')
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



# 生成邀请码
@csrf_exempt
def invite_url(request,proj_id):
    """
    1. 校验前端表单中数据合法性
    2. 判断创建邀请人的人是否为项目创建者
    3. 若是，则生成邀请码保存在数据库中（即，此邀请码有效）
    """
    form = ProjectInviteModelForm(data=request.POST)
    if form.is_valid():
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period','无权创建邀请码!')
            return JsonResponse({'status':False,'errors':form.errors.get_json_data()})
        invite_code = uid(request.tracer.user.phone)
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.instance.code = invite_code
        form.save()

        # 邀请码url链接
        url = f'{request.scheme}://{request.get_host()}{reverse('web:invite_join',kwargs={'code':invite_code})}'
        return JsonResponse({'status':True,'url':url})
    return JsonResponse({'status':False,'errors':form.errors.get_json_data()})






# 访问邀请码链接地址
def invite_join(request,code):
    invite_obj = models.ProjectInvite.objects.filter(code=code).first()
    # 邀请码是否存在
    if not invite_obj:
        return render(request, 'invite_join.html', {'errors': '邀请码不存在'})

    # 邀请码是否已过期
    current_datetime = datetime.datetime.now()
    limit_datetime = invite_obj.create_datetime + timedelta(minutes=invite_obj.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'errors': '邀请码已过期'})

    # 访问人是否是项目创建者
    if request.tracer.user == invite_obj.project.creator:
        return render(request, 'invite_join.html', {'errors': '创建者无需再加入项目'})

    # 访问人是否是项目参与者
    if models.Participants.objects.filter(project=invite_obj.project,user=request.tracer.user).exists():
        return render(request, 'invite_join.html', {'errors': '已加入项目无需再加入'})

    # 该项目人数是否超出订阅范围
    product_obj = models.Subscribe.objects.filter(user=invite_obj.creator).first().product
    if invite_obj.project.join_count+1 > product_obj.max_member:
        return render(request, 'invite_join.html', {'errors': '项目成员超限'})

    # 邀请码能够使用的次数是否用完
    if invite_obj.count:
        if invite_obj.use_count >= invite_obj.count:
            return render(request, 'invite_join.html', {'errors': '邀请码次数已使用完'})

    invite_obj.use_count += 1
    invite_obj.save()
    invite_obj.project.join_count += 1
    invite_obj.project.save()
    models.Participants.objects.create(project=invite_obj.project,user=request.tracer.user)
    return render(request,'invite_join.html',{'project':invite_obj.project})









