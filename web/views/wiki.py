from django.http import JsonResponse

from web import models
from web.forms.wiki import WikiModelForm

from django.urls import reverse
from django.shortcuts import render, redirect



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
        # 判断新增wiki是不是子文章，如果是则深度加一
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project_id = proj_id
        form.save()
        url = reverse('web:wiki',kwargs={'proj_id':proj_id})
        return redirect(url)
    return render(request,'wiki_add.html',{'form':form})



# def wiki_catalog(request,proj_id):
#     wikis = models.Wiki.objects.filter(project_id=proj_id).order_by('depth','id')
#     return JsonResponse({'status':True,'data':wikis})
