from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from redis.commands.timeseries import GET_CMD

from app01.forms.account import SendSmsForm, RegisterForm


# Create your views here.

def send_sms(request):
    form = SendSmsForm(request,data=request.GET)
    if form.is_valid():
        return JsonResponse({'status':True})
    return JsonResponse({'status':False,'error':form.errors.get_json_data()})


def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        if form.is_valid():
            return HttpResponse('成功')
        return JsonResponse({'status':False,'error':form.errors.get_json_data()})
    return render(request, 'app01/register.html', {'form': form})

