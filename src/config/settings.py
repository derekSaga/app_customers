from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Exemplo com SQLite assíncrono. Para Postgres use: postgresql+asyncpg://...
    DATABASE_URL: str = "sqlite+aiosqlite:///./customers.db"
    DATABASE_SCHEMA: str = "customer"
    ECHO_SQL: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
