"""
Application Configuration Management.

This module uses `pydantic-settings` to manage the application's configuration.
Settings are loaded from environment variables and a `.env` file.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Defines the application's configuration settings.

    This class loads settings from environment variables and a `.env` file.
    It centralizes all configuration parameters, making them accessible
    through a single `settings` object.

    Attributes:
        DATABASE_URL: The connection string for the database.
            Example for async SQLite: "sqlite+aiosqlite:///./customers.db"
            Example for async PostgreSQL: "postgresql+asyncpg://user:pass@host/db"
        DATABASE_SCHEMA: The default schema to be used for database tables.
        ECHO_SQL: If True, SQLAlchemy will log all generated SQL statements.
        LOG_LEVEL: The logging level for the application 
            (e.g., "INFO", "DEBUG").
        PUBSUB_PROJECT_ID: The Google Cloud Project ID for Pub/Sub.
        REDIS_HOST: The hostname or IP address of the Redis server.
        REDIS_PORT: The port number for the Redis server.
        REDIS_DB: The database number to use in Redis.
        CUSTOMER_CREATE_TOPIC: The name of the Pub/Sub topic for customer
            creation events.
        CUSTOMER_CREATE_TOPIC_SUBSCRIPTION: The name of the Pub/Sub
            subscription for the customer creation topic.
    """

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./customers.db"
    DATABASE_SCHEMA: str = "customer"
    ECHO_SQL: bool = True

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Google Cloud Pub/Sub settings
    PUBSUB_PROJECT_ID: str = "test-project"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # Topic and Subscription names
    CUSTOMER_CREATE_TOPIC: str = Field(default="command.create.customer")
    CUSTOMER_CREATE_TOPIC_SUBSCRIPTION: str = Field(
        default="command.create.customer.app_customer.sub"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
