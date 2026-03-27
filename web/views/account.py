import uuid
import datetime
from io import BytesIO

from utils.image_code import check_code
from web import models
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm, LoginForm


# 发送短信
def send_sms(request):
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})


# 获取图片验证码
def img_code(request):
    img_obj, code = check_code()
    stream = BytesIO()
    img_obj.save(stream, 'png')
    request.session.clear_expired()
    request.session['img_code'] = code
    request.session.set_expiry(60)
    return HttpResponse(stream.getvalue())


# 注册
def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # 用户表中注册新用户
        instance = form.save()

        # 新用户添加免费版订阅
        product_obj = models.Product.objects.filter(category=1, name='个人免费版').first()
        models.Subscribe.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            product=product_obj,
            user=instance, count=0,
            price=0,
            start_time=datetime.datetime.now()
        )
        url = reverse('web:login')
        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})


# 短信登录
def login_sms(request):
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'login_sms.html', {'form': form})

    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        user_obj = form.cleaned_data.get('phone')
        request.session['user_id'] = user_obj.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        url = reverse('web:project_list')
        return JsonResponse({'status': True, 'data': url})
    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})


# 密码登录
def login(request):
    if request.method == "GET":
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        # 表单验证通过(图片验证码对比成功）
        # 进行手机号/邮箱和密码的比对
        phone_or_email = form.cleaned_data.get('phone_or_email')
        pwd = form.cleaned_data.get('pwd')
        user_obj = models.User.objects.filter(
            Q(phone=phone_or_email) | Q(email=phone_or_email)).filter(
            pwd=pwd).first()

        if user_obj:
            # 登录成功后恢复session的有效期
            request.session['user_id'] = user_obj.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect('web:project_list')
        form.add_error('phone_or_email', '手机/邮箱与密码不匹配')
    return render(request, 'login.html', {'form': form})


# 退出登录
def logout(request):
    request.session.flush()
    return redirect('web:index')
