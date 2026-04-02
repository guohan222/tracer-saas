from django import forms
from web import models
from web.forms.bootstrap import Bootstrap

from django.core.exceptions import ValidationError


class FileModelForm(Bootstrap, forms.ModelForm):

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