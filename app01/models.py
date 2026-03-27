from datetime import timedelta

from django.db import models


# Create your models here.

# 用户表
class User(models.Model):
    name = models.CharField(verbose_name='用户名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    pwd = models.CharField(verbose_name='密码', max_length=128)
    phone = models.CharField(verbose_name='手机号', max_length=32)
    inviter = models.ForeignKey('User',verbose_name='邀请者',on_delete=models.SET_NULL,null=True,blank=True)


# 产品表
class Product(models.Model):
    name = models.CharField(verbose_name='产品名', max_length=32, unique=True)
    money = models.IntegerField(verbose_name='价格/年')
    max_project = models.IntegerField(verbose_name='允许最大项目个数')
    max_member = models.IntegerField(verbose_name='允许最多成员')
    max_storage = models.PositiveIntegerField(verbose_name='项目最大存储空间')
    max_send = models.PositiveIntegerField(verbose_name='单次上传文件最大限制')


# 订阅表
class Subscribe(models.Model):
    status = models.BooleanField(verbose_name='订阅状态')
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)
    user = models.ForeignKey('User', verbose_name='用户', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', verbose_name='产品', default=1, on_delete=models.SET_NULL, null=True,
                                   blank=True)
    numbers = models.IntegerField(verbose_name='购买个数', default=0)
    money = models.IntegerField(verbose_name='实际支付金额', default=0)
    start_time = models.DateTimeField(verbose_name='购买时间', auto_now_add=True)
    stop_time = models.DateTimeField(verbose_name='订阅结束时间', null=True, blank=True)

    # 覆盖父类的save方法实现，控制存储过程（在保存前执行自定义操作）
    def save(self, *args, **kwargs):
        if self.numbers:
            data = 365 * self.numbers
            self.stop_time = self.start_time + timedelta(days=data)
        super().save(*args, **kwargs)


# 项目表
class Project(models.Model):
    name = models.CharField(verbose_name='项目名称', max_length=32)
    color = models.CharField(verbose_name='项目颜色', max_length=32)
    describe = models.TextField(verbose_name='项目描述')
    user = models.ForeignKey('User', verbose_name='项目创建者', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标项目', default=False)
    people = models.IntegerField(verbose_name='参与人数')
    used_storage = models.PositiveIntegerField(verbose_name='已使用的存储空间')


# 项目参与者表
class Participants(models.Model):
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name='参加者', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标项目', default=False)
