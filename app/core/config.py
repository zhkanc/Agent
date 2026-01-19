from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "qwen-plus"
    log_level: str = "info"
    dashscope_api_key: str = Field(..., alias="DASHSCOPE_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
