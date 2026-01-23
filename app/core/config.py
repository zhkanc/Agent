from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()
    model_name: str = "qwen-plus"
    log_level: str = "info"
    llm_concurrency_limit: int = 5
    dashscope_api_key: str = Field(..., alias="DASHSCOPE_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
