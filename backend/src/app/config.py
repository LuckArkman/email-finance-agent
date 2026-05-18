from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvironmentSettings(BaseSettings):
    project_name: str = "AI Email Finance Agent"
    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/finance_agent"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "finance_agent_docs"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"
    aws_access_key_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = "sustentacodigo_verify_me"
    whatsapp_phone_number_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str = "finance-agent-documents"
    openai_api_key: str = ""
    sentry_dsn: str = ""
    
    jwt_secret_key: str = "super_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # OAuth2 (Gmail, Outlook)
    google_client_id: str = "577377971527-5vm404s6ufia4dv3b0mejregpsh7vocv.apps.googleusercontent.com"
    google_client_secret: str = "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"
    google_redirect_uri: str = "http://localhost:8000/api/v1/emails/callback/google"
    
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    microsoft_redirect_uri: str = "http://localhost:8000/api/v1/emails/callback/outlook"

    frontend_base_url: str = "http://localhost"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class BaseAPIConfig:
    @staticmethod
    def get_settings() -> EnvironmentSettings:
        return EnvironmentSettings()
