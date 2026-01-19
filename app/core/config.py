from pydantic import BaseSettings


class Settings(BaseSettings):
    model_name: str = "qwen-plus"
    log_level: str = "info"

    class Config:
        env_file = ".env"


settings = Settings()
