from django import forms
from web import models
from web.forms.bootstrap import Bootstrap
from utils.tencent.cos import check_file

from django.core.exceptions import ValidationError



class FolderModelForm(Bootstrap, forms.ModelForm):

    class Meta:
        model = models.FileRepository
        fields = ('name',)
        
    def __init__(self,request,parent_obj, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request
        self.parent_obj =parent_obj

    def clean_name(self):
        name = self.cleaned_data.get('name')
        file_obj = models.FileRepository.objects.filter(project=self.request.tracer.project,file_type=2,name=name,parent=self.parent_obj).exists()
        if file_obj:
            raise ValidationError('该目录下已有同名文件夹')
        return name



class FileModelForm(forms.ModelForm):
    ETag = forms.CharField(label='Etag')
    class Meta:
        model = models.FileRepository
        exclude = ['project', 'file_type', 'update_user', 'update_datetime']


    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request


    def clean_file_path(self):
        return f'https://{self.cleaned_data['file_path']}'


    def clean(self):
        key = self.cleaned_data['key']
        etag = self.cleaned_data['ETag']
        size = self.cleaned_data['file_size']

        if not key or not etag:
            return self.cleaned_data

        # 向COS校验文件是否合法
        # SDK的功能
        from qcloud_cos.cos_exception import CosServiceError
        try:
            result = check_file(self.request.tracer.project.bucket, self.request.tracer.project.region, key)
        except CosServiceError as e:
            self.add_error("key", '文件不存在')
            return self.cleaned_data

        cos_etag = result.get('ETag')
        if etag != cos_etag:
            self.add_error('etag', 'ETag错误')

        cos_length = result.get('Content-Length')
        if int(cos_length) != size:
            self.add_error('size', '文件大小错误')

        return self.cleaned_data


