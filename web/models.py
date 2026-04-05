from datetime import timedelta

from django.db import models


# Create your models here.

# 用户表
class User(models.Model):
    name = models.CharField(verbose_name='用户名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    pwd = models.CharField(verbose_name='密码', max_length=128)
    phone = models.CharField(verbose_name='手机号', max_length=32, unique=True)
    # inviter = models.ForeignKey('User', verbose_name='邀请者', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


# 产品表
class Product(models.Model):
    category_choice = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choice)
    name = models.CharField(verbose_name='产品名', max_length=32, unique=True)
    money = models.IntegerField(verbose_name='价格/年')
    max_project = models.IntegerField(verbose_name='允许最大项目个数')
    max_member = models.IntegerField(verbose_name='允许最多成员')
    max_storage = models.PositiveIntegerField(verbose_name='单项目最大存储空间', help_text='G')
    max_send = models.PositiveIntegerField(verbose_name='单次上传文件最大限制', help_text='M')

    cate_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# 订阅表
class Subscribe(models.Model):
    status_choice = (
        (1, '未支付'),
        (2, '已支付'),
    )
    status = models.SmallIntegerField(verbose_name='订阅状态', choices=status_choice)
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)  # 唯一索引
    product = models.ForeignKey('Product', verbose_name='产品', default=1, on_delete=models.SET_NULL, null=True,
                                blank=True)
    user = models.ForeignKey('User', verbose_name='用户', on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='购买个数', default=0)
    price = models.IntegerField(verbose_name='实际支付金额', default=0)

    # 允许为空，因为可能是未支付状态，不能给开始时间
    start_time = models.DateTimeField(verbose_name='购买时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='订阅结束时间', null=True, blank=True)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 覆盖父类的save方法实现，控制存储过程（在保存前执行自定义操作）
    def save(self, *args, **kwargs):
        if self.count:
            data = 365 * self.count
            self.stop_time = self.start_time + timedelta(days=data)
        super().save(*args, **kwargs)


# 项目表
class Project(models.Model):
    color_choice = (
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc6563'),
        (4, '#a2d148'),
        (5, '#20BFA4'),
        (6, '#7461c2'),
        (7, '#20bfa3'),
    )
    name = models.CharField(verbose_name='项目名称', max_length=32)
    color = models.SmallIntegerField(verbose_name='项目颜色', choices=color_choice, default=1)
    describe = models.TextField(verbose_name='项目描述', null=True, blank=True)
    star = models.BooleanField(verbose_name='星标项目', default=False)
    used_storage = models.BigIntegerField(verbose_name='已使用的存储空间', default=0, help_text='字节')

    creator = models.ForeignKey('User', verbose_name='项目创建者', on_delete=models.CASCADE)
    join_count = models.IntegerField(verbose_name='参与人数', default=1)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='cos桶名', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=32)


# 项目参与者表
class Participants(models.Model):
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name='参加者', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标项目', default=False)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# wiki表
class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='所属项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='文章名', max_length=32)
    content = models.TextField(verbose_name='文章内容')
    depth = models.IntegerField(verbose_name='深度', default=1)

    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='children')

    def __str__(self):
        return self.title


# 文件管理表
class FileRepository(models.Model):
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹'),
    )

    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    name = models.CharField(verbose_name='文件夹名称', max_length=32, help_text='文件/文件夹名称')
    key = models.CharField(verbose_name='cos中名称', max_length=128, null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True, help_text='字节')
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name='父目录', to='FileRepository', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='children')

    update_user = models.ForeignKey(verbose_name='最近更新者', to='User', on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


# 问题总表
class Issues(models.Model):
    project = models.ForeignKey(verbose_name='所属项目', to='Project', on_delete=models.CASCADE)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name='所属工期', to='Module', on_delete=models.CASCADE, null=True, blank=True)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ('danger', '高'),
        ('warning', '中'),
        ('success', '低'),
    )
    priority = models.CharField(verbose_name='优先级', max_length=32, choices=priority_choices, default='danger')

    # 问题状态
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新开工'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    assign = models.ForeignKey(verbose_name='指派', to='User', related_name='task', on_delete=models.CASCADE, null=True,
                               blank=True)
    attention = models.ManyToManyField(verbose_name='关注者', to='User', related_name='observer', blank=True)

    start_date = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式')
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='children', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='User', related_name='create_problems',
                                on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject




# 问题里程杯表
class Module(models.Model):
    """解释：某个问题属于某个阶段工期里面的"""
    title = models.CharField(verbose_name='工期名称', max_length=32)
    project = models.ForeignKey(verbose_name='所属项目', to='Project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# 问题类型表
class IssuesType(models.Model):
    """如：任务、功能、bug"""
    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='所属项目', to='Project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
