

from django.http import JsonResponse
from django.shortcuts import render
from web.forms.issues import IssuesModelForm

def issues(request,proj_id):
    if request.method == "GET":
        form = IssuesModelForm(request)
        return render(request,'issues.html',{'form':form})

    form = IssuesModelForm(request,data=request.POST)
    if form.is_valid():
        # exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        form.instance.project_id = proj_id
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'errors':form.errors.get_json_data()})