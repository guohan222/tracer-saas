from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from utils.tencent.cos import credential

from app01.forms.account import SendSmsForm, RegisterForm, ProjectForm


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
    return render(request, 'app01/layout/basic.html', {'form': form})


def account(request):
    return render(request, 'app01/account.html')


def create_project(request):
    form = ProjectForm()
    if request.method == 'POST':
        if form.is_valid():
            pass
    return render(request, 'app01/register.html', {'form': form})



def upload(request):
    return render(request,'app01/upload_test.html')



def test_credential(request):
    key = request.GET.get('filename')

    # 2. 获取字典数据
    result = credential('17340563297-1775050064-1412810729', 'ap-guangzhou', key)

    # 3. 修正返回方式：把 HttpResponse 换成 JsonResponse
    return JsonResponse(result)


