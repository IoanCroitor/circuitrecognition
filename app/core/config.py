import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Circuit Recognition API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key-for-development")
    API_KEY_HEADER: str = "X-API-Key"
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png"]
    ALLOWED_ASC_TYPES: List[str] = ["text/plain"]
    
    # Model settings
    MODEL_PATH: str = "best_weights.pt"
    YOLOV5_PATH: str = "yolov5-master"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    class Config:
        case_sensitive = True

settings = Settings()