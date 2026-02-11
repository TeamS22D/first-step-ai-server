from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY: str
    INTERNAL_JWT_SECRET: str

    APP_NAME: str = "FirstStepAI"
    DEBUG: bool = True
    FASTAPI_URL: str = "http://localhost:8000"

config = Config()
