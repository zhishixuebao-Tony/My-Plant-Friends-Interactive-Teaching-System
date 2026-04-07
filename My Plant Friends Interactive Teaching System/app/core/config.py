import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "??????????????"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    ALIYUN_AK: str = os.getenv("ALIYUN_AK", "")
    ALIYUN_SK: str = os.getenv("ALIYUN_SK", "")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", "")
    OSS_BUCKET_NAME: str = os.getenv("OSS_BUCKET_NAME", "")
    OSS_FOLDER: str = os.getenv("OSS_FOLDER", "")

    STUDENT_ROSTER: dict = {f"{i:02d}": f"??{i:02d}" for i in range(1, 51)}
    PRELOAD_MEDIA: dict = {f"{i:02d}": f"https://via.placeholder.com/300?text=Plant_{i}" for i in range(1, 51)}

    COZE_API_KEY: str = os.getenv("COZE_API_KEY", "")
    COZE_AGENT_ID: str = os.getenv("COZE_AGENT_ID", "")
    COZE_API_ENDPOINT: str = os.getenv("COZE_API_ENDPOINT", "https://api.coze.cn/v1/chat/completions")


settings = Settings()
