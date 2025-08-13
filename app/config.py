from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "telecom_plans"
    product_catalog_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
