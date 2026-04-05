from django.http import JsonResponse
from django.shortcuts import render

from utils.tencent.cos import delete_bucket
from web import models




def settings(request,proj_id):
    return render(request,'settings.html')


# 删除项目
def settings_del(request,proj_id):
    if request.method == "GET":
        return render(request,'settings_del.html')

    proj_name = request.POST.get('project_name')
    if not proj_name or request.tracer.project.name != proj_name:
        return JsonResponse({'status':False,'error':'请正确输入当前项目名称!'})

    # 只允许项目创建者进行删除
    if request.tracer.user != request.tracer.project.creator:
        return JsonResponse({'status':False,'error':'您非该项目创建者，无权删除!'})

    # 1. 删除桶
    #       - 删除桶中的所有文件（找到桶中的所有文件 + 删除文件 )
    #       - 删除桶中的所有碎片（找到桶中的所有碎片 + 删除碎片 )
    #       - 删除桶
    delete_bucket(request.tracer.project.bucket, request.tracer.project.region)

    # 2. 删除项目
    #       - 项目删除
    models.Project.objects.filter(id=proj_id).delete()
    return JsonResponse({'status':True})



