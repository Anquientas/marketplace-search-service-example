from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_connection_string: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5435
    postgres_database_name: str = "search_db"
    postgres_username: str = "postgres"
    postgres_password: str = "postgres"

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", validation_alias="KAFKA_BROKERS"
    )
    kafka_topic_ads: str = "ads"
    kafka_consumer_group: str = "search-service"

    ad_service_url: str = "http://localhost:8002"

    @property
    def database_url(self) -> str:
        if self.postgres_connection_string:
            return self.postgres_connection_string
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_username}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_database_name}"
        )
