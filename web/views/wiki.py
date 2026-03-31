from web import models
from web.forms.wiki import WikiModelForm

from django.urls import reverse
from django.shortcuts import render, redirect


# wiki菜单首页
def wiki(request, proj_id):
    wiki_id = request.GET.get('wiki_id')

    # 判断是否要查看文章
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_obj = models.Wiki.objects.filter(project_id=proj_id, id=wiki_id).first()
    return render(request, 'wiki.html', {'wiki_obj': wiki_obj})


# 添加wiki
def wiki_add(request, proj_id):

    if request.method == 'GET':
        form = WikiModelForm(proj_id)
        return render(request, 'wiki_form.html', {'form': form})

    form = WikiModelForm(proj_id, data=request.POST)
    if form.is_valid():
        # 判断新增wiki是不是子文章，如果是则深度加一
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project_id = proj_id
        form.save()
        url = reverse('web:wiki', kwargs={'proj_id': proj_id})
        return redirect(url)
    return render(request, 'wiki_form.html', {'form': form})


# 删除wiki
def wiki_del(request, proj_id):
    wiki_id = request.GET.get('wiki_id')
    models.Wiki.objects.filter(project_id=proj_id, id=wiki_id).delete()
    url = reverse('web:wiki', kwargs={'proj_id': proj_id})
    return redirect(url)


# 编辑wiki
def wiki_edit(request, proj_id):
    wiki_id = request.GET.get('wiki_id')
    wiki_obj = models.Wiki.objects.filter(project_id=proj_id, id=wiki_id).first()

    if not wiki_obj:
        url = reverse('web:wiki', kwargs={'proj_id': proj_id})
        return redirect(url)

    if request.method == 'GET':
        form = WikiModelForm(proj_id, instance=wiki_obj)
        return render(request, 'wiki_form.html', {'form': form})

    form = WikiModelForm(proj_id, data=request.POST, instance=wiki_obj)
    if form.is_valid():
        # 判断新增wiki是不是子文章，如果是则深度加一
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project_id = proj_id
        form.save()

        # 返回到编辑好的wiki文章页面
        url = reverse('web:wiki', kwargs={'proj_id': proj_id})
        preview = f'{url}?wiki_id={wiki_id}'
        return redirect(preview)

    return render(request, 'wiki_form.html', {'form': form})
