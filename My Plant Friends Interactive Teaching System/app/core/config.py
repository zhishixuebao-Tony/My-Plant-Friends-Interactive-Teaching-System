# 文件：app/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "三年级语文习作：我的植物朋友"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    # --- 必须确保下面这 5 行存在，且名字与 oss_service.py 调用的完全一致 ---
    ALIYUN_AK: str = os.getenv("ALIYUN_AK", "")
    ALIYUN_SK: str = os.getenv("ALIYUN_SK", "")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", "")
    OSS_BUCKET_NAME: str = os.getenv("OSS_BUCKET_NAME", "")
    OSS_FOLDER: str = os.getenv("OSS_FOLDER", "")
    # --------------------------------------------------------------

    # 学生名单，格式为：{"01": "学生01", "02": "学生02", ...}
    STUDENT_ROSTER: dict = {f"{i:02d}": f"学生{i:02d}" for i in range(1, 51)}
    
    # 预加载的图片，格式为：{"01": "https://xxx.jpg", "02": "https://xxx.jpg", ...}
    PRELOAD_MEDIA: dict = {f"{i:02d}": f"https://via.placeholder.com/300?text=Plant_{i}" for i in range(1, 51)}

    # 别忘了这个（如果你要测环节3）
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

settings = Settings()