import time
from web import models
from web.forms.project import CreateProjectForm

from utils.tencent.cos import create_bucket

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse


# 展示项目与创建项目
def project_list(request):
    """项目列表"""
    if request.method == 'GET':
        form = CreateProjectForm(request)
        # 待展示的项目数据
        project_dict = {'star':[],'my':[],'join':[]}
        # 我创建的项目
        my_list = models.Project.objects.filter(creator=request.tracer.user)
        for item in my_list:
            if item.star:
                project_dict['star'].append({'type':'my','proj':item})
            else:
                project_dict['my'].append(item)
        # 我参加的项目
        join_list = models.Participants.objects.filter(user=request.tracer.user)
        for item in join_list:
            if item.star:
                project_dict['star'].append({'type':'join','proj':item.project})
            else:
                project_dict['join'].append(item.project)

        return render(request,'project_list.html',{'form':form,'project_dict':project_dict})

    form = CreateProjectForm(request,data=request.POST)
    if form.is_valid():
        # 为新建的项目创建桶
        name = form.cleaned_data['name']
        bucket = f'{request.tracer.user.phone}-{int(time.time())}-1412810729'
        region = 'ap-guangzhou'
        create_bucket(bucket,region)

        # 创建项目
        form.instance.bucket = bucket
        form.instance.region = region
        form.instance.creator = request.tracer.user
        instance = form.save()

        # 为项目初始化几个问题类型
        """
        models.IssuesType.object.create(project_id=proj_id,title='xxx')
        等价于
        obj = models.IssuesType(project_id=proj_id,title='xxx')     # 实例化IssuesType对象
        obj.save()                                                  # 将这个对象写入数据库对应的表中
            
        """
        issues_obj_list = []
        for item in models.IssuesType.PROJECT_INIT_LIST:
            issues_obj_list.append(models.IssuesType(title=item,project_id=instance.id))
        models.IssuesType.objects.bulk_create(issues_obj_list)

        return JsonResponse({'status':True})

    return JsonResponse({'status':False, 'form':form.errors})


# 添加星标项目
def project_star(request,proj_type,proj_id):
    if proj_type == 'my':
        models.Project.objects.filter(creator=request.tracer.user,id=proj_id).update(star=True)
        return redirect('web:project_list')
    if proj_type == 'join':
        models.Participants.objects.filter(user=request.tracer.user,project_id=proj_id).update(star=True)
        return redirect('web:project_list')
    return HttpResponse('请求错误')


# 取消星标项目
def project_unstar(request,proj_type,proj_id):
    if proj_type == 'my':
        models.Project.objects.filter(creator=request.tracer.user, id=proj_id).update(star=False)
        return redirect('web:project_list')
    if proj_type == 'join':
        models.Participants.objects.filter(user=request.tracer.user,project_id=proj_id).update(star=False)
        return redirect('web:project_list')
    return HttpResponse('请求错误')
