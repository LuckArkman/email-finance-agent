from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvironmentSettings(BaseSettings):
    project_name: str = "AI Email Finance Agent"
    environment: str = "development"
    debug: bool = True
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "finance_agent_docs"
    redis_url: str = "redis://localhost:6379/0"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str = "finance-agent-documents"
    openai_api_key: str = ""
    
    jwt_secret_key: str = "super_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class BaseAPIConfig:
    @staticmethod
    def get_settings() -> EnvironmentSettings:
        return EnvironmentSettings()
