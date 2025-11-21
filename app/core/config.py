from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


    APP_NAME: str = "FirstStepAI"
    DEBUG: bool = True
    OPENAI_API_KEY: str


config = Config()
