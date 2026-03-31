from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = ''
secret_key = ''
region = 'ap-guangzhou'      # 替换为用户的 region，已创建桶归属的 region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)



"""
# 创建桶
response = client.create_bucket(
    Bucket='9',
    ACL = 'public-read'          # private私有读写   public-read    public-read-write
)

# 向桶中上传文件
response = client.upload_file(
    Bucket='p29',
    LocalFilePath='1.png',      # 本地文件的路径
    Key='picture.jpg',          # 上传到桶之后的文件名
    PartSize=1,
    MAXThread=10,
    EnableMD5=False
)

"""

