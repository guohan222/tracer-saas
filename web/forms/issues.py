
from web import models
from web.forms.bootstrap import Bootstrap
from django import forms




class IssuesModelForm(Bootstrap,forms.ModelForm):

    class Meta:
        model = models.Issues
        exclude =  ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            'assign':forms.Select(attrs={'class':'tom-select-single'}),
            'parent':forms.Select(attrs={'class':'tom-select-single'}),
            'attention':forms.SelectMultiple(attrs={'class':'tom-select-multiple'}),
            'start_date': forms.DateInput(attrs={'class': 'date-picker', 'autocomplete': 'off'}),
            'end_date': forms.DateInput(attrs={'class': 'date-picker', 'autocomplete': 'off'}),
            'desc': forms.Textarea(attrs={'class': 'vditor-textarea'}),
        }


    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

        # 数据的合理性选择

        # 1. 限制问题类型只能选择该项目拥有的问题类型
        type_list = []      # 数据库中不允许不选择
        type_obj_list = models.IssuesType.objects.filter(project_id=request.tracer.project.id).values_list('id','title')
        type_list.extend(type_obj_list)
        self.fields['issues_type'].choices = type_list

        # 2. 限制问题所属工期只能选择该项目拥有的工期
        module_list = [('','没有选择任何项')]
        module_obj_list = models.Module.objects.filter(project_id=request.tracer.project.id).values_list('id','title')
        module_list.extend(module_obj_list)
        self.fields['module'].choices = module_list

        # 3. 限制问题指派和关注中只能选择该项目的参与者和创建者
            # 项目创建者
        user_list = [(request.tracer.project.creator.id,request.tracer.project.creator.name)]
            # 项目参与者
        user_obj_list = models.Participants.objects.filter(project_id=request.tracer.project.id).values_list('user_id','user__name')
        user_list.extend(user_obj_list)
        self.fields['assign'].choices = [('','没有选择任何项')] + user_list
        self.fields['attention'].choices = user_list

        # 4. 限制父问题只能选择该项目中的问题
        parent_list = [('','没有选择任何项')]
        parent_obj_list = models.Issues.objects.filter(project_id=request.tracer.project.id).values_list('id','subject')
        parent_list.extend(parent_obj_list)
        self.fields['parent'].choices = parent_list




class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ('content','parent')

