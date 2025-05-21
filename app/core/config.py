"""
Application configuration.
"""
from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, field_validator, PostgresDsn, validator
from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Universal Knowledge Graph"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (List, str)):
            return v
        raise ValueError(v)

    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nexus_ukg"
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: str = "AAImBVT1BB4fgrKXyKnnxM46lRUJ97PLCwJh4gZOwdhnpKM1JzucJQQJ99BCACHYHv6XJ3w3AAAAACOGw5OW"
    AZURE_OPENAI_ENDPOINT: str = "https://kevin-m8961u8a-eastus2.cognitiveservices.azure.com"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4.1"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    
    # LLM Settings
    LLM_PROVIDER: str = "azure"  # "azure" or "openai"
    LLM_DEFAULT_TEMPERATURE: float = 0.3
    LLM_DEFAULT_MAX_TOKENS: int = 1000
    LLM_DEFAULT_SYSTEM_PROMPT: str = """You are an expert AI agent specializing in knowledge graph operations and reasoning.
Your task is to analyze nodes, apply algorithms, and make decisions about knowledge relationships.
You should:
1. Carefully analyze input data and context
2. Apply domain-specific reasoning
3. Consider confidence levels and uncertainty
4. Suggest improvements or additional processing when needed
5. Maintain a clear trace of your reasoning process"""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 