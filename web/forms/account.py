import redis

from web import models
from utils.alibaba import sms
from django_redis import get_redis_connection
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError




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



class SendSmsForm(forms.Form):
    # 发送短信之前校验手机格式是否非空（forms.CharField等字段默认require=True）和是否满足正则表达式
    phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机号格式错误'), ])
    def clean_phone(self):
        # 检测注册时数据库是否有了该手机
        phone = self.cleaned_data.get('phone')
        res = models.User.objects.filter(phone=phone)
        if res:
            raise ValidationError('手机号已存在!')
        tpl = self.request.GET.get('tpl')
        sms_tpl_id = settings.SMS_TEMPLATE_ID.get(tpl)
        if not sms_tpl_id:
            raise ValidationError('短信模板不存在!')
        # 发送短信
        sms_ret = sms.send_verify_code(phone,sms_tpl_id)
        if not sms_ret.body.success:
            raise ValidationError(f'短信发送失败:{sms_ret.body.message}')

        # 写入redis
        conn = get_redis_connection()
        conn.set(phone,sms_ret.body.code,ex=60)


        # self.cleaned_data['sms_tpl_id'] = sms_tpl_id
        return phone

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request