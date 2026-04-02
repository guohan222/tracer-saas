from web import models
from web.forms.file import FileModelForm

from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse


def file(request, proj_id):
    """文件列表&添加文件"""

    # 文件页面url情况
    # 根目录：http://127.0.0.1:8000/manage/19/file/
    # 子目录：http://127.0.0.1:8000/manage/19/file/?folder=1    进入了folder

    # 当前所处的目录
    parent_obj = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_obj = models.FileRepository.objects.filter(id=folder_id, file_type=2,
                                                          project=request.tracer.project.id).first()

    # GET请求查看文件页面
    if request.method == 'GET':
        # 文件导航
        breadcrumb_list = []
        parent = parent_obj
        while parent:
            # breadcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent

        # 当前目录下的所有文件
        data_list = models.FileRepository.objects.filter(project=request.tracer.project.id, parent=parent_obj).order_by(
            '-file_type')
        form = FileModelForm(request,parent_obj)

        content = {
            'breadcrumb_list': breadcrumb_list,
            'data_list': data_list,
            'form': form
        }
        return render(request, 'file.html', content)

    # POST请求添加文件/编辑文件夹

    # 判断是新建文件夹还是编辑文件夹
    fid = request.POST.get('fid','')
    edit_obj = None
    if fid.isdecimal():
        edit_obj = models.FileRepository.objects.filter(id=fid, project=request.tracer.project.id, file_type=2).first()
    if edit_obj:
        form = FileModelForm(request, parent_obj, data=request.POST, instance=edit_obj)
    else:
        form = FileModelForm(request, parent_obj, data=request.POST)

    if form.is_valid():
        form.instance.project_id = proj_id
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'form': form.errors.get_json_data()})
