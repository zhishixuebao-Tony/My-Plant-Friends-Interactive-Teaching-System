import oss2
import uuid
from app.core.config import settings

def get_presigned_url(student_id: str, file_extension: str, module_name: str) -> dict:
    """
    【前端直传模式 - 增强修复版】
    生成阿里云 OSS 的 PUT 预签名 URL，并锁定 Content-Type 解决签名不匹配问题。
    """
    
    # 1. 认证初始化 (从 settings 读取 5 把钥匙)
    auth = oss2.Auth(settings.ALIYUN_AK, settings.ALIYUN_SK)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
    
    # 2. 生成唯一的、防重名的文件名
    # 格式：student_id_随机8位字符.jpg (例如: 01_a1b2c3d4.jpg)
    random_hex = uuid.uuid4().hex[:8]
    file_name = f"{student_id}_{random_hex}.{file_extension}"
    
    # 3. 构造云端存储路径 (按文件夹结构分类)
    # 最终路径格式: [OSS_FOLDER]/[环节名]/[文件名]
    # 示例: yuwen-2026/stage2_record/01_abc123.jpg
    folder = settings.OSS_FOLDER.rstrip('/') if settings.OSS_FOLDER else "uploads"
    object_key = f"{folder}/{module_name}/{file_name}"
    
    # 4. 【关键步骤】锁定请求头
    # 阿里云签名校验非常严格，后端签发时指定的 Header 必须与前端上传时带的一模一样。
    # 这里我们统一规定图片上传必须带 'Content-Type': 'image/jpeg'
    headers = {
        'Content-Type': 'image/jpeg'
    }

    # 5. 生成预签名 PUT URL
    # headers 参数必须传入，否则上传时带 Content-Type 会报 SignatureDoesNotMatch
    put_url = bucket.sign_url(
        method='PUT', 
        key=object_key, 
        expires=3600,  # 有效期 1 小时
        headers=headers
    )
    
    # 6. 生成上传成功后的永久公网访问地址
    # 格式: https://[Bucket名].[Endpoint]/[文件路径]
    access_url = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{object_key}"
    
    return {
        "upload_url": put_url,    # 发送给前端，用于直接上传文件
        "access_url": access_url,   # 发送给前端，上传成功后把这个 URL 发回给 Python 存库
        "object_key": object_key,   # 仅供调试查看路径
        "content_type": "image/jpeg" # 告知前端上传时必须带的 Header
    }

# 文件：app/services/oss_service.py

#生成查看链接的函数
def get_view_url(file_path: str) -> str:
    """
    生成一个带签名的 GET 预览链接，有效期 1 小时。
    file_path 是文件在 OSS 上的完整路径，如 "yuwen-20260325/封面图.jpg"
    """
    auth = oss2.Auth(settings.ALIYUN_AK, settings.ALIYUN_SK)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
    
    # 生成预览链接
    # params 设为 inline 确保浏览器尝试直接打开而不是下载
    params = {'response-content-disposition': 'inline'}
    sign_url = bucket.sign_url('GET', file_path, 3600, params=params)
    
    return sign_url