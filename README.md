# Tracer - 轻量级级多租户 SaaS 项目协作平台

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.10-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)](https://getbootstrap.com/)
[![Tencent COS](https://img.shields.io/badge/Tencent-COS-orange.svg)](https://cloud.tencent.com/product/cos)


## 项目简介

Tracer 是一套完整的 SaaS 形态项目协作系统。项目基于 Django 4.2 开发，核心攻克了 SaaS 架构下的**多租户数据隔离**与**动态鉴权**难题。业务层实现了基于角色的项目管理、问题追踪及文档协作；底层深度集成腾讯云 COS 实现分布式文件存储，并打通了支付宝支付 API，独立完成了包含价格策略、订单状态机、回调验签的完整支付订阅系统。具备一套标准化 SaaS 平台应有的高可用、易扩展特性。


## 核心亮点 

* **🏢 SaaS 多租户架构与数据隔离**
  * 基于 `project_id` 的强数据隔离，保证不同团队间的数据绝对安全。
  * 细粒度的角色与权限控制，动态生成 ModelForm 数据源，防止越权访问。
* **💳 完整的商业化支付闭环**
  * 深度对接支付宝开放平台（电脑网站支付）。
  * 实现从生成订单、扫码支付、到回调验签（RSA2）的全链路逻辑。
  * 具备动态套餐配额控制，按支付状态实时限制项目数、存储空间等资源池。
* **📊 敏捷项目问题追踪 (Issue Tracker)**
  * 支持多维度的复杂条件筛选（问题类型、状态、优先级、指派人等）。
  * 动态表单渲染，Markdown 富文本即时预览与存储。
* **☁️ 分布式对象存储 (Tencent COS)**
  * 抛弃本地存储，对接腾讯云 COS，实现云端文件管理与网盘功能。
  * 结合前后端实现大文件安全直传，减轻应用服务器带宽压力。
* **📚 云端协作知识库 (Wiki)**
  * 支持无限层级的目录树状结构渲染。
  * 文档防并发覆盖与版本管理基础支撑。


## 技术栈

### 后端

- Python 3.13
- Django 4.2.10
- MySQL
- Redis（用于缓存和验证码存储）

### 前端

- Bootstrap 5.3.0
- JavaScript 
- Highcharts（数据可视化）
- Flatpickr（日期选择器）
- editormd / Vditor（Markdown编辑器）

### 第三方服务

- 腾讯云COS（对象存储）
- 阿里云短信服务（验证码发送）
- 支付宝开放平台 (Alipay API)


## 项目结构

```
tracer/
├── web/                  # 主要应用目录
│   ├── forms/            # 表单定义
│   ├── middlewares/      # 中间件
│   ├── migrations/       # 数据库迁移文件
│   ├── static/           # 静态文件
│   ├── templates/        # 模板文件
│   ├── views/            # 视图函数
│   ├── admin.py          # 后台管理
│   ├── apps.py           # 应用配置
│   ├── models.py         # 数据模型
│   └── urls.py           # URL配置
├── tracer/               # 项目配置目录
│   ├── __init__.py
│   ├── asgi.py
│   ├── local_settings.py # 本地配置
│   ├── settings.py       # 全局配置
│   ├── urls.py           # 全局URL配置
│   └── wsgi.py
├── utils/                # 工具函数目录
│   ├── alibaba/          # 阿里云相关
│   ├── tencent/          # 腾讯云相关
│   ├── encrypt.py        # 加密功能
│   ├── image_code.py     # 图片验证码
│   ├── order.py          # 订单相关
│   └── pagination.py     # 分页功能
├── scripts/              # 脚本文件目录
├── files/                # 文件存储目录
├── manage.py             # 管理脚本
└── requirements.txt      # 依赖文件
```


## 核心模块

### 1. 认证模块

- 实现用户注册、登录、权限控制
- 支持短信验证码和图片验证码
- 使用Redis存储验证码

### 2. 项目模块

- 项目的创建、编辑、删除
- 项目星标管理
- 项目成员管理和邀请码系统

### 3. Issues模块

- 问题的创建、编辑、评论
- 问题状态和优先级管理
- 问题筛选和搜索

### 4. 文件模块

- 文件和文件夹的管理
- 腾讯云COS存储集成
- 存储空间管理

### 5. Wiki模块

- Markdown文档编辑
- 文档层级结构
- 图片上传

### 6. 仪表盘模块

- 项目概览数据
- 问题状态分布
- 项目成员信息

### 7. 统计模块

- 问题趋势图表
- 人员工作进度统计
- 优先级分布统计

### 8. 订阅模块

- 产品套餐管理
- 支付宝支付集成
- 余额抵扣机制




## 📸 界面预览 
<img width="2541" height="1064" alt="Image" src="https://github.com/user-attachments/assets/6463ab56-c4b6-42a7-8a41-28c080ca1678" />
<img width="2560" height="1238" alt="Image" src="https://github.com/user-attachments/assets/9abce485-6155-475f-8909-98e7ecfe9f83" />
<img width="2552" height="795" alt="Image" src="https://github.com/user-attachments/assets/9d93f84d-70bf-4d2b-81be-52d4eb54879f" />
<img width="2551" height="1241" alt="Image" src="https://github.com/user-attachments/assets/ba83cc3f-2d74-4a0d-9e01-921de907e3aa" />
<img width="2560" height="1238" alt="Image" src="https://github.com/user-attachments/assets/bca96df9-8567-47dd-a8f9-cad5269186e4" />
<img width="2553" height="665" alt="Image" src="https://github.com/user-attachments/assets/02e31045-701b-4949-b210-b888fb91b695" />
<img width="2543" height="672" alt="Image" src="https://github.com/user-attachments/assets/3b400545-775d-4806-b9e5-a8da191b2b20" />
<img width="2247" height="995" alt="Image" src="https://github.com/user-attachments/assets/cb22921a-41ba-4c74-aa91-b5e7f8e4be13" />
<img width="2120" height="766" alt="Image" src="https://github.com/user-attachments/assets/7bf77197-24af-4d27-9f3b-ed0386322ae3" />
<img width="1989" height="931" alt="Image" src="https://github.com/user-attachments/assets/a4954215-cb31-443a-94d4-04661afd305c" />
<img width="1798" height="497" alt="Image" src="https://github.com/user-attachments/assets/0d1037d0-6cf5-4e12-b650-e7d6878e06ab" />
<img width="1747" height="574" alt="Image" src="https://github.com/user-attachments/assets/e70d727f-80d2-41bb-87dd-cd56e917f2cf" />





## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

 `local_settings.py`填写相关配置：

- 数据库配置(DATABASES)
- Redis配置(CACHES)
- 腾讯云COS配置(TENCENT_COS_ID, TENCENT_COS_KEY, 等)
- 阿里云短信服务配置(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, 等)
- 支付宝密钥路径 (ALI_PRI_KEY_PATH, ALI_PUB_KEY_PATH - 指向本地安全的 .txt 文件)


## 联系方式

- 微信：guohan2o
- 邮箱：guohan0826@gmail.com
- GitHub：[guohan222](https://github.com/guohan222)

---

**Tracer** - 让项目管理更简单、更高效！
        
