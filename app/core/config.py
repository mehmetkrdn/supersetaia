from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Superset Security Gateway"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str

    SECRET_KEY: str = "CHANGE_ME_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    NORTHWIND_DB_HOST: str = "localhost"
    NORTHWIND_DB_PORT: int = 5432
    NORTHWIND_DB_NAME: str = "northwind"
    NORTHWIND_DB_USER: str = "postgres"
    NORTHWIND_DB_PASSWORD: str = "postgres"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()