
---

## Step 6: Create src/config.py

```python
"""Configuration management for MongoDB Retail Agent"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Google Cloud
    google_cloud_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    google_cloud_region: str = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    
    # Gemini & Agent Builder
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    agent_id: str = os.getenv("AGENT_ID", "")
    model_id: str = os.getenv("MODEL_ID", "gemini-3-pro")
    
    # MongoDB
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "retail_db")
    mongodb_inventory_collection: str = os.getenv("MONGODB_COLLECTION_INVENTORY", "inventory")
    mongodb_customers_collection: str = os.getenv("MONGODB_COLLECTION_CUSTOMERS", "customers")
    mongodb_orders_collection: str = os.getenv("MONGODB_COLLECTION_ORDERS", "orders")
    
    # Application
    app_name: str = "MongoDB Retail Agent"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    environment: str = os.getenv("FLASK_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # GitLab
    gitlab_token: Optional[str] = os.getenv("GITLAB_TOKEN")
    gitlab_project_id: Optional[str] = os.getenv("GITLAB_PROJECT_ID")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings
settings = get_settings()
