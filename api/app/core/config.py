from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

class _Settings(BaseModel):
    model_config = {"protected_namespaces": ()}
    allowed_origins: List[str] = [os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")]
    api_port: int = int(os.getenv("API_PORT", "8000"))
    model_name: str = os.getenv("MODEL_NAME", "qwen2.5-math-7b")
    model_api_base: str = os.getenv("MODEL_API_BASE", "")
    model_api_key: str = os.getenv("MODEL_API_KEY", "")

settings = _Settings()
