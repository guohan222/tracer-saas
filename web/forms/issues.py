
from web import models
from web.forms.bootstrap import Bootstrap
from django import forms




class IssuesModelForm(Bootstrap,forms.ModelForm):

    class Meta:
        model = models.Issues
        exclude =  ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            'assign':forms.Select(attrs={'class':'tom-select-single'}),
            'attention':forms.SelectMultiple(attrs={'class':'tom-select-multiple'}),
            'start_date': forms.DateInput(attrs={'class': 'date-picker', 'autocomplete': 'off'}),
            'end_date': forms.DateInput(attrs={'class': 'date-picker', 'autocomplete': 'off'}),
            'desc': forms.Textarea(attrs={'class': 'vditor-textarea'}),
        }


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
