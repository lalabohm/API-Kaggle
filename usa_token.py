from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    kaggle_username: str
    kaggle_key: str

    class Config:
        env_file = ".env"

settings = Settings()
