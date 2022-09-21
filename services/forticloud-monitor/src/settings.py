from typing import List, Optional

from pydantic import BaseSettings, Field

from clients import NatsSettings
from usecases.check_device import DeviceConsumerSettings


class Settings(BaseSettings):
    environment: str = Field("production", env="CURRENT_ENVIRONMENT")
    environment_name: str = Field(..., env="ENVIRONMENT_NAME")
    papertrail_active: bool = Field(True, env="PAPERTRAIL_ACTIVE")
    papertrail_host: Optional[str] = Field(None, env="PAPERTRAIL_HOST")
    papertrail_port: Optional[int] = Field(None, env="PAPERTRAIL_PORT")
    papertrail_prefix: Optional[str] = Field(None, env="PAPERTRAIL_PREFIX")
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    nats_servers: List[str] = Field(..., env="NATS_SERVERS")
    bruin_base_url: str = Field(..., env="BRUIN_BASE_URL")
    device_consumer_queue: str = "forticloud-monitor"
    device_consumer_subject: str = "forticloud.monitored-devices"

    @property
    def is_papertrail_active(self) -> bool:
        return (
            self.is_production
            and self.papertrail_active
            and self.papertrail_host
            and self.papertrail_port
            and self.papertrail_prefix
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def nats(self) -> NatsSettings:
        return NatsSettings(servers=self.nats_servers)

    @property
    def device_consumer(self) -> DeviceConsumerSettings:
        return DeviceConsumerSettings(queue=self.device_consumer_queue, subject=self.device_consumer_subject)
