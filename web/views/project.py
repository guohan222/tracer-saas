from web.forms.project import CreateProjectForm

from django.shortcuts import render
from django.http import JsonResponse


# 新建项目
def project_list(request):
    if request.method == 'GET':
        form = CreateProjectForm(request)
        return render(request,'project_list.html',{'form':form})
    form = CreateProjectForm(request,data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'form':form.errors})