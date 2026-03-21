from django.http import HttpResponse
from django.shortcuts import render
from utils.alibaba import sms
from django.conf import settings



# Create your views here.

def send(request):
    tpl = request.GET.get('tpl')
    sms_tpl_id = settings.SMS_TEMPLATE_ID.get(tpl)
    if not sms_tpl_id:
        return HttpResponse('模板ID不存在')
    ret = sms.send_verify_code('1377330232', sms_tpl_id)
    if ret.body.success:
        return HttpResponse('成功')
    else:
        return HttpResponse(ret.body.message)



