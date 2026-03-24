import re
from django.shortcuts import render
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSmsForm
from django.http import JsonResponse
from django.conf import settings
from utils.alibaba import sms


def send_sms(request):
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})


def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})


def login_sms(request):
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'login_sms.html', {'form': form})

    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        user_obj = form.cleaned_data.get('phone')
        return JsonResponse({'status': True, 'data': '666'})
    return JsonResponse({'status': False, 'error': form.errors.get_json_data()})
