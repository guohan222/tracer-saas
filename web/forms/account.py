import random
import json

import requests

from utils import encrypt
from web import models
from utils.alibaba import sms
from web.forms.bootstrap import Bootstrap
from django import forms
from django.db.models import Q
from django_redis import get_redis_connection
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# 注册
class RegisterModelForm(Bootstrap, forms.ModelForm):
    pwd = forms.CharField(label='密码', min_length=8, max_length=64,
                          error_messages={'min_length': '重复密码不能小于8个字符',
                                          'max_length': '重复密码不能大于64个字符'},
                          widget=forms.PasswordInput())
    confirm_pwd = forms.CharField(label='重复密码', min_length=8, max_length=64,
                                  error_messages={'min_length': '重复密码不能小于8个字符',
                                                  'max_length': '重复密码不能大于64个字符'},
                                  widget=forms.PasswordInput())
    phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机号格式错误'), ])
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.User
        fields = ('name', 'email', 'pwd', 'confirm_pwd', 'phone')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        exist = models.User.objects.filter(name=name).exists()
        if exist:
            self.add_error('name', '用户名已存在!')
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exist = models.User.objects.filter(email=email).exists()
        if exist:
            self.add_error('email', '邮箱已存在!')
        return email

    def clean_pwd(self):
        pwd = self.cleaned_data.get('pwd')
        return encrypt.md5(pwd)

    def clean_confirm_pwd(self):
        confirm_pwd = self.cleaned_data.get('confirm_pwd')
        if encrypt.md5(confirm_pwd) != self.cleaned_data.get('pwd'):
            self.add_error('confirm_pwd', '两次输入的密码不一致!')
        return confirm_pwd

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        exist = models.User.objects.filter(phone=phone).exists()
        if exist:
            self.add_error('phone', '手机已存在!')
        return phone

    def clean_code(self):
        code = self.cleaned_data.get('code')
        phone = self.cleaned_data.get('phone')

        conn = get_redis_connection()
        redis_code = conn.get(phone)

        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送!')

        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            self.add_error('code', '验证码不正确,请重新输入')

        # 阿里的校验
        # if not sms.check_verify_code(phone,code).body.model.verify_result:
        #     self.add_error('code', '验证码不正确,请重新输入')
        return code


# 发送短信
class SendSmsForm(forms.Form):
    phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机号格式错误'), ])

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        tpl = self.request.GET.get('tpl')
        sms_tpl_id = settings.SMS_TEMPLATE_ID.get(tpl)
        if not sms_tpl_id:
            raise ValidationError('短信模板不存在!')

        res = models.User.objects.filter(phone=phone)
        if tpl == 'register':
            if res:
                raise ValidationError('手机号已存在!')
        else:
            if not res:
                raise ValidationError('手机号不存在!')

        # 自定义短信
        code = json.dumps(random.randint(1000, 9999))
        sms_ret = sms.send_verify_code(phone, sms_tpl_id, code)
        # 利用阿里的短信
        # sms_ret = sms.send_verify_code(phone, sms_tpl_id)

        if not sms_ret.body.success:
            raise ValidationError(f'短信发送失败:{sms_ret.body.message}')

        # 写入redis
        conn = get_redis_connection()
        conn.set(phone, code, ex=60)

        return phone

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


# 短信登录
class LoginSmsForm(Bootstrap, forms.Form):
    phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$', '手机号格式错误'), ])
    code = forms.CharField(label='验证码')

    def clean_phone(self):
        """phone字段级校验通过后检查手机号是否在数据库中"""
        phone = self.cleaned_data.get('phone')
        user_obj = models.User.objects.filter(phone=phone).first()
        if not user_obj:
            raise ValidationError('手机号不存在!')
        return user_obj

    def clean_code(self):
        code = self.cleaned_data.get('code')

        # 防止phone字段级校验不通过:不执行clean_phone，避免后续无法点出phone属性
        user_obj = self.cleaned_data.get('phone')
        if not user_obj:
            return code

        phone = user_obj.phone
        # 获取验证码
        conn = get_redis_connection()
        redis_code = conn.get(phone)

        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送!')
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            self.add_error('code', '验证码不正确,请重新输入')
        return code


# 密码登录
class LoginForm(Bootstrap, forms.Form):
    """
    进行手机号/邮箱存在的判断
    进行图片验证码的对比
    不进行手机/邮箱跟密码对比（在调用处进行对比，方便获取用户）

    """
    phone_or_email = forms.CharField(label='手机号或邮箱')
    pwd = forms.CharField(label='密码', min_length=8, max_length=64,
                          error_messages={'min_length': '重复密码不能小于8个字符',
                                          'max_length': '重复密码不能大于64个字符'},
                          widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='验证码')

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_pwd(self):
        pwd = self.cleaned_data.get('pwd')
        return encrypt.md5(pwd)


    def clean_code(self):
        code = self.cleaned_data.get('code')
        session_code = self.request.session.get('img_code')
        if not session_code:
            raise ValidationError('图片验证码失效,请重新获取!')
        if session_code.upper() != code.upper():
            raise ValidationError('图片验证码错误,请重新输入!')
        return code

