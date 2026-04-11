import json
import datetime

from web import models

from utils.alibaba.alipay import AliPay
from utils.encrypt import uid

from django.conf import settings
from django_redis import get_redis_connection

from django.http import HttpResponse
from django.shortcuts import render, redirect


# 官网首页
def index(request):
    return render(request,'index.html')



# 订阅产品展示
def price(request):
    # 获取产品
    product_list = models.Product.objects.filter(category=2)
    return render(request,'price.html',{'product_list':product_list})



# 支付页面
def payment(request,product_id):
    # 获取用户选择的产品信息
    prod_obj = models.Product.objects.filter(category=2,id=product_id).first()

    # 获取用户的购买数量
    number = request.GET.get('number','')
    if not number or not number.isdecimal():
        return redirect('web:price')

    number = int(number)
    if number < 1:
        return redirect('web:price')

    # 算出原价格
    origin_price = prod_obj.money * number

    """
    用户如果在使用收费版本期间购买其他高级收费版本：
    1. 计算原收费版本平均每天的收费价格
    2. 将还未使用的天数乘以这个平均的价格，将此价格作为该用户购买新产品时的抵扣价
    """
    balance = 0
    subscribe_obj = None

    # 获取该用户正在使用的产品的交易记录
    if request.tracer.product.category == 2:
        subscribe_obj = models.Subscribe.objects.filter(status=2,user=request.tracer.user).order_by('-id').first()
        total_timedelta= subscribe_obj.end_time - subscribe_obj.start_time
        balance_timedelta = subscribe_obj.end_time - datetime.datetime.now()

        # 如果用户当天购买了2种产品,也算它最先买的产品使用了一天
        if balance_timedelta.days == total_timedelta.days:
            balance = subscribe_obj.price / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = subscribe_obj.price / total_timedelta.days * balance_timedelta.days

    # 避免优惠价格大于原价格
    if balance >= origin_price:
        return redirect('web:price')

    # 用户准备购买的信息
    content = {
        'prod_obj_id':prod_obj.id,
        'subscribe_obj_id':subscribe_obj.id if subscribe_obj else None,
        'number':number,
        'origin_price':origin_price,
        'balance':balance,
        'total_price':origin_price - round(balance,2)
    }
    # 存储该信息（http协议：无状态）
    conn = get_redis_connection()
    key = f'payment_{request.tracer.user.phone}'
    conn.set(key,json.dumps(content),ex=60*30)

    content['prod_obj'] = prod_obj
    content['subscribe_obj'] = subscribe_obj

    return render(request,'payment.html',content)




# 生成交易记录（未支付），跳转至支付宝页面
def pay(request):
    """
    之前之所以将其搞到redis中，是因为http协议是无状态的
    从之前的url过来访问这个url，无法区分是否是同一个人，所以应将这个人的初始订单信息与这个人进行设置绑定即用到redis，以后通过设置的key即可拿到相关信息

    """
    conn = get_redis_connection()
    key = f'payment_{request.tracer.user.phone}'
    content_byte = conn.get(key)
    if not content_byte:
        return redirect('web:price')
    content = json.loads(content_byte.decode('utf-8'))

    # 创建交易记录（未支付）
    order_id = uid(request.tracer.user.phone)
    total_price = content['total_price']
    models.Subscribe.objects.create(
        status=1,
        order=order_id,
        product_id=content['prod_obj_id'],
        user=request.tracer.user,
        count=content['number'],
        price=total_price
    )

    # 进行接口url的配置
    ali_pay = AliPay(
        appid = settings.ALI_APPID,
        return_url = settings.ALI_RETURN_URL,
        app_notify_url = settings.ALI_NOTIFY_URL,
        app_private_key_path = settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path = settings.ALI_PUB_KEY_PATH
    )
    query_params = ali_pay.direct_pay(
        subject='Tracer-payment',
        out_trade_no=order_id,
        total_amount=total_price
    )

    # 跳转到支付宝支付页面
    pay_url = f'{settings.ALI_GATEWAY}?{query_params}'
    return redirect(pay_url)





# 支付成功后POST请求的url视图
def pay_notify(request):
    ali_pay = AliPay(
        appid=settings.ALI_APPID,
        return_url=settings.ALI_RETURN_URL,
        app_notify_url=settings.ALI_NOTIFY_URL,
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )

    if request.method == 'GET':
        """
        1. 用户跳转过来后，只判断支付是否成功，不做订单的妆台更新
        2. 跳转过来时，支付宝会把之前设置的订单id也返回
        3. 根据签名判断，是否真从支付宝跳转过来（利用支付宝公钥
        
        """
        params = request.GET.dict()
        sign = params.pop('sign')
        status = ali_pay.verify(params, sign)
        if status:
            current_datetime = datetime.datetime.now()
            out_trade_no = params['out_trade_no']
            _object = models.Subscribe.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_datetime = current_datetime
            _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('支付完成')
        return HttpResponse('支付失败')

    else:
        """
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        sign = post_dict.pop('sign', None)
        status = ali_pay.verify(post_dict, sign)
        if status:
            current_datetime = datetime.datetime.now()
            out_trade_no = post_dict['out_trade_no']
            _object = models.Subscribe.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_time = current_datetime
            _object.end_time = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('success')

        return HttpResponse('error')
        """