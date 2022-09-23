from typing import Optional

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    environment: str = Field("local", env="CURRENT_ENVIRONMENT")
    environment_name: str = Field("local", env="ENVIRONMENT_NAME")
    health_server_port: int = Field(5000, env="HEALTH_SERVER_PORT")
    papertrail_active: Optional[bool] = Field(True, env="PAPERTRAIL_ACTIVE")
    papertrail_host: Optional[str] = Field(None, env="PAPERTRAIL_HOST")
    papertrail_port: Optional[int] = Field(None, env="PAPERTRAIL_PORT")
    papertrail_prefix: Optional[str] = Field(None, env="PAPERTRAIL_PREFIX")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_papertrail_active(self) -> bool:
        return (
            self.is_production
            and self.papertrail_active
            and self.papertrail_host
            and self.papertrail_port
            and self.papertrail_prefix
        )
