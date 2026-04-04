import json

from web import models
from web.forms.file import FolderModelForm, FileModelForm
from utils.tencent import cos

from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# 展示文件&文件夹导航、新增&编辑文件夹
def file(request, proj_id):
    """文件列表&添加、编辑文件"""

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
        form = FolderModelForm(request, parent_obj)

        content = {
            'breadcrumb_list': breadcrumb_list,
            'data_list': data_list,
            'form': form,
            'parent_id': folder_id
        }
        return render(request, 'file.html', content)

    # POST请求添加文件/编辑文件夹

    # 判断是新建文件夹还是编辑文件夹
    fid = request.POST.get('fid', '')
    edit_obj = None
    if fid.isdecimal():
        edit_obj = models.FileRepository.objects.filter(id=fid, project=request.tracer.project.id, file_type=2).first()
    if edit_obj:
        form = FolderModelForm(request, parent_obj, data=request.POST, instance=edit_obj)
    else:
        form = FolderModelForm(request, parent_obj, data=request.POST)

    if form.is_valid():
        form.instance.project_id = proj_id
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'form': form.errors.get_json_data()})


# 删除文件
def file_del(request, proj_id):
    del_id = request.GET.get('del_id')
    del_obj = models.FileRepository.objects.filter(project_id=proj_id, id=del_id).first()

    # 用户删除单个文件
    if del_obj.file_type == 1:
        # 删除文件归还用户在该项目使用的空间
        request.tracer.project.used_storage -= del_obj.file_size
        request.tracer.project.save()

        # cos中删除文件
        cos.del_file(request.tracer.project.bucket, request.tracer.project.region, del_obj.key)

        # 在数据库中删除该文件
        del_obj.delete()
        return JsonResponse({'status': True})

    # 用户删除整个目录
    files_size = 0
    key_list = []
    folder_list = []
    for folder in folder_list:
        children_list = models.FileRepository.objects.filter(project_id=proj_id, parent=folder).order_by('-file_type')
        for item in children_list:
            if item.file_type == 2:
                folder_list.append(item)
            else:
                files_size += item.file_size
                key_list.append({'key': item.key})

    if key_list:
        cos.del_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)

    if files_size:
        request.tracer.project.used_storage -= del_obj.file_size
        request.tracer.project.save()

    # 在数据库中删除该文件
    del_obj.delete()
    return JsonResponse({'status': True})


# 获取凭证
@csrf_exempt
def upload_credential(request, proj_id):
    # 该产品单项目最大存储空间 G
    total_file_limit = request.tracer.product.max_storage * 1024 * 1024 * 1024
    # 该产品单次上传文件大小限制 MB
    send_file_limit = request.tracer.product.max_send * 1024 * 1024

    # 文件列表 [{name,size},]
    check_file_list = json.loads(request.body.decode('utf-8'))
    # 总文件大小
    total_size = 0
    for item in check_file_list:
        if item['size'] > send_file_limit:
            msg = f'单文件上传超出限制（最大{request.tracer.product.max_send}M），文件：{item['size']}，请升级套餐!'
            return JsonResponse({'status': False, 'error': msg})
        else:
            total_size += item['size']

    # 该项目已使用的存储空间
    used_storage = request.tracer.project.used_storage
    if total_size + used_storage > total_file_limit:
        return JsonResponse({'status': False, 'error': "该项目容量超过限制，请升级套餐！"})

    credential_data = cos.credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({'status': True, 'credential_data': credential_data})


# 添加前端向cos上传成功的文件信息
@csrf_exempt
def file_add(request, proj_id):
    """
    body: JSON.stringify({
        "name": file.name,
        "key": key,
        "file_size": file.size,
        "file_path": uploadData.Location,  （桶.cos.区域.myqcloud.com/图片路径）
        "parent": current_folder_id,
        "ETag": uploadData.Etag
    })
    """

    data = json.loads(request.body.decode('utf-8'))
    form = FileModelForm(request,data=data)
    if form.is_valid():
        """
        form.instance.project_id = proj_id
        form.instance.file_type = 1
        instance = form.save()
        # 通过ModelForm保存到数据库中的数据返回的instance对象，无法通过get_choice字段_display获取choice中的中文
        # 即无法通过instance.get_file_type_display获取file_type的中文
        """

        # 清洗过后的数据
        new_data = form.cleaned_data
        new_data.pop('ETag')
        new_data.update({'project_id':proj_id,'file_type':1,'update_user_id':request.tracer.user.id})
        instance = models.FileRepository.objects.create(**new_data)
        # 减少该项目存储空间
        request.tracer.project.used_storage += new_data['file_size']
        request.tracer.project.save()
        return JsonResponse({'status':True})
    print(form.errors)
    return JsonResponse({'status':False,'error':form.errors.get_json_data()})


