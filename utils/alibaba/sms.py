# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import json

from django.conf import settings

from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredentialConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models

# from alibabacloud_tea_util.client import Client as UtilClient
# from alibabacloud_credentials.utils.auth_util import client_type




def send_verify_code(phone, tpl_code, code):
    """
    自定义函数，封装阿里短信认证发送请求
    短信模板参数使用阿里定义的，不用传入

    :param phone:手机号
    :param tpl_code:短信模板
    :param code:自定义验证码
    :return:
    """
    credentialsconfig = CredentialConfig(
        type='access_key',
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
    )
    credentialsclient = CredentialClient(credentialsconfig)
    config = open_api_models.Config(credential=credentialsclient, endpoint="dypnsapi.aliyuncs.com")
    client = Dypnsapi20170525Client(config)

    send_sms_verify_code_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
        sign_name='速通互联验证码',
        template_code=tpl_code,
        phone_number=phone,
        template_param=json.dumps({"code":code,"min":"1"})
    )
    runtime = util_models.RuntimeOptions()
    resp = client.send_sms_verify_code_with_options(send_sms_verify_code_request, runtime)
    return resp


def check_verify_code(phone, verify_code):
    """
    自定义函数，封装阿里短信认证发送请求
    短信模板参数使用阿里定义的，不用传入

    :param phone:手机号
    :param verify_code:短信码
    :return:
    """
    credentialsconfig = CredentialConfig(
        type='access_key',
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
    )
    credentialsclient = CredentialClient(credentialsconfig)
    config = open_api_models.Config(credential=credentialsclient, endpoint="dypnsapi.aliyuncs.com")
    client = Dypnsapi20170525Client(config)

    check_sms_verify_code_request = dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(phone_number=phone,
                                                                                       verify_code=verify_code)

    runtime = util_models.RuntimeOptions()
    resp = client.check_sms_verify_code_with_options(check_sms_verify_code_request, runtime)
    return resp
