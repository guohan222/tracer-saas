from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from django.conf import settings


# 创建桶
def create_bucket(bucket,region='ap-guangzhou'):
    """
    创建桶
    :param bucket: 桶名
    :param region: 区域
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # private私有读写   public-read    public-read-write
    )

    # 为桶设置跨域访问规则
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }

    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )




# 上传文件
def upload_file(bucket,region,file_obj,key):
    """
    上传文件
    :param bucket: 桶名
    :param region: 区域
    :param file_obj: 文件对象
    :param key: cos中的文件名
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_obj,  # 待上传的文件对象
        Key=key,  # 上传到桶之后的文件名
    )

    return f'https://{bucket}.cos.{region}.myqcloud.com/{key}'




# 获取凭证
def credential(bucket, region, key=None):
    """ 获取cos上传临时凭证 """
    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        # 固定密钥 id
        'secret_id': settings.TENCENT_COS_ID,
        # 固定密钥 key
        'secret_key': settings.TENCENT_COS_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀
        'allow_prefix': '*',
        # 密钥的权限列表
        'allow_actions': [
            # 简单上传
            "name/cos:PutObject",
            # 分块上传
            "name/cos:InitiateMultipartUpload",
            "name/cos:ListMultipartUploads",
            "name/cos:ListParts",
            "name/cos:UploadPart",
            "name/cos:CompleteMultipartUpload",
        ],
    }

    sts = Sts(config)
    response = sts.get_credential()
    credential_dic = dict(response)
    credential_info = credential_dic.get("credentials")

    credential_data = {
        "bucket": config.get("bucket"),
        "region": config.get("region"),
        "key": key,
        "startTime": credential_dic.get("startTime"),
        "expiredTime": credential_dic.get("expiredTime"),
        "requestId": credential_dic.get("requestId"),
        "expiration": credential_dic.get("expiration"),
        "credentials": {
            "tmpSecretId": credential_info.get("tmpSecretId"),
            "tmpSecretKey": credential_info.get("tmpSecretKey"),
            "sessionToken": credential_info.get("sessionToken"),
        },
    }

    return credential_data




# 删除文件
def del_file(bucket,region,key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key
    )





# 删除多个文件
def del_file_list(bucket,region,key_list):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    objects = key_list
    client.delete_objects(
        Bucket=bucket,
        Delete={
            'Object': objects
        }
    )