
from web import models
from web.forms.bootstrap import Bootstrap

from django import forms

class WikiModelForm(Bootstrap,forms.ModelForm):

    class Meta:
        model = models.Wiki
        exclude = ('project','depth')

    def __init__(self,proj_id,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.proj_id = proj_id

        # 给要展示的字段绑定指定数据（避免该项目wiki父文章这一栏有不属于该项目的wiki）
        total_data_list = [('','请选择')]
        data_list = models.Wiki.objects.filter(project_id=proj_id).values_list('id','title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
