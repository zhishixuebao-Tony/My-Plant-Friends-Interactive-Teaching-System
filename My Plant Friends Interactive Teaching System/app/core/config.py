import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    PROJECT_NAME: str = "??????????????"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    STUDENT_ROSTER: dict = {f"{i:02d}": f"??{i:02d}" for i in range(1, 51)}
    PRELOAD_MEDIA: dict = {f"{i:02d}": "" for i in range(1, 51)}
    LOCAL_MEDIA_DIR: str = os.getenv("LOCAL_MEDIA_DIR", str(PROJECT_ROOT / "local_media"))
    LOCAL_MEDIA_URL_PREFIX: str = os.getenv("LOCAL_MEDIA_URL_PREFIX", "/local-media")

settings = Settings()
