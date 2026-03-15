from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvironmentSettings(BaseSettings):
    project_name: str = "AI Email Finance Agent"
    environment: str = "development"
    debug: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class BaseAPIConfig:
    @staticmethod
    def get_settings() -> EnvironmentSettings:
        return EnvironmentSettings()
