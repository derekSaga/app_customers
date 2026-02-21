from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Exemplo com SQLite assíncrono. Para Postgres use: postgresql+asyncpg://...
    DATABASE_URL: str = "sqlite+aiosqlite:///./customers.db"
    DATABASE_SCHEMA: str = "customer"
    ECHO_SQL: bool = True
    LOG_LEVEL: str = "INFO"
    PUBSUB_PROJECT_ID: str = Field(...)
    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CUSTOMER_CREATE_TOPIC: str = Field(default="command.create.customer")
    CUSTOMER_CREATE_TOPIC_SUBSCRIPTION: str = Field(
        default="command.create.customer.app_customer.sub"
    )


settings = Settings()  # type: ignore[call-arg]
