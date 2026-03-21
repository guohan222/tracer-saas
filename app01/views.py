from django.http import HttpResponse
from django.shortcuts import render
from utils.alibaba import sms
# Create your views here.

def send(request):
    ret = sms.send_verify_code('1377330232',100001)
    print(ret)
    return HttpResponse('成功')