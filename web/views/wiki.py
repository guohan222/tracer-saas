from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from web.forms.wiki import WikiModelForm


# wiki菜单首页
def wiki(request,proj_id):
    return render(request,'wiki.html')


# 添加wiki
def wiki_add(request,proj_id):
    if request.method == 'GET':
        form = WikiModelForm(proj_id)
        return render(request,'wiki_add.html',{'form':form})
    form = WikiModelForm(proj_id,data=request.POST)
    if form.is_valid():
        form.instance.project_id = proj_id
        form.save()
        url = reverse('web:wiki',kwargs={'proj_id':proj_id})
        return redirect(url)
    return render(request,'wiki_add.html',{'form':form})
