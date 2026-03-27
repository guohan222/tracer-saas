from itertools import product

from web.forms.bootstrap import Bootstrap
from web import models
from django import forms
from django.core.exceptions import ValidationError


class CreateProjectForm(Bootstrap,forms.ModelForm):

    class Meta:
        model = models.Project
        fields = (
            'name',
            'color',
            'describe',
        )
        widgets = {
            'describe':forms.Textarea
        }

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    """
    1. 该用户不能创建重名的项目
    2. 该用户对订阅的使用情况还允不允许它再新建
    
    
    """
    def clean_name(self):
        name = self.cleaned_data.get('name')
        user_obj = self.request.tracer.user
        product_obj = self.request.tracer.product
        exists = models.Project.objects.filter(name=name,creator=user_obj).exists()
        if exists:
            raise ValidationError('该项目名正在被您使用!')
        nums = models.Project.objects.filter(creator=user_obj).count()
        if nums >= product_obj.max_project:
            raise ValidationError('项目数量超出订阅范围，请升级订阅!')

        return name







