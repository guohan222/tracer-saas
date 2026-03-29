
from web import models
from web.forms.project import CreateProjectForm
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse


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
                project_dict['star'].append({'type':'my','proj':item.project})
            else:
                project_dict['my'].append(item.project)

        return render(request,'project_list.html',{'form':form,'project_dict':project_dict})

    form = CreateProjectForm(request,data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.save()
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
