import re
from django.shortcuts import render
from web.forms.account import RegisterForm, SendSmsForm
from django.http import JsonResponse
from django.conf import settings
from utils.alibaba import sms



def send_sms(request):
    form = SendSmsForm(request,data=request.GET)
    if form.is_valid():
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'error':form.errors.get_json_data()})


def register(request):
    if request.method == 'GET':
        form  = RegisterForm()
        return render(request,'register.html',{'form':form})
    form = RegisterForm(data=request.POST)

    if form.is_valid():
        form.save()
        return JsonResponse({'status':True,'data':'/login/'})
    return JsonResponse({'status':False,'error':form.errors.get_json_data()})