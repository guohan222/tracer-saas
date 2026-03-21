import re

from django.db.models.expressions import result
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from utils.alibaba import sms
from django.conf import settings
from django import forms
from app01 import models
from django.core.validators import RegexValidator


# Create your views here.

def send_sms(request):
    tpl = request.GET.get('tpl')
    phone = request.GET.get('user_phone')
    res = re.match(r'^1[3|4|5|6|7|8|9]\d{9}$',phone)
    sms_tpl_id = settings.SMS_TEMPLATE_ID.get(tpl)
    ret = sms.send_verify_code(phone, sms_tpl_id)
    if res and sms_tpl_id:
        return JsonResponse({'code':200,'msg':ret.body.message})
    else:
        return JsonResponse({'code':400,'msg':ret.body.message})


class RegisterForm(forms.ModelForm):
    pwd = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_pwd = forms.CharField(label='重复密码', widget=forms.PasswordInput())
    phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机号格式错误'), ])
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.User
        fields = ('name', 'email', 'pwd', 'confirm_pwd', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'请输入{field.label}'


def register(request):
    form = RegisterForm()
    return render(request, 'app01/register.html', {'form': form})

