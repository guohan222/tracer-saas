from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from django.conf import settings


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



def upload_file(bucket,region,file_obj,key):

    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_obj,  # 待上传的文件对象
        Key=key,  # 上传到桶之后的文件名
    )

    return f'https://{bucket}.cos.{region}.myqcloud.com/{key}'