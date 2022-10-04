from typing import Optional

from bruin_client import BruinCredentials
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from pydantic import BaseSettings, Field

from application.clients import NatsSettings
from application.consumers import ConsumerSettings


class Config(BaseSettings):
    environment: str = Field("local", env="CURRENT_ENVIRONMENT")
    environment_name: str = Field("local", env="ENVIRONMENT_NAME")
    papertrail_active: Optional[bool] = Field(True, env="PAPERTRAIL_ACTIVE")
    papertrail_host: Optional[str] = Field(None, env="PAPERTRAIL_HOST")
    papertrail_port: Optional[int] = Field(None, env="PAPERTRAIL_PORT")
    papertrail_prefix: Optional[str] = Field(None, env="PAPERTRAIL_PREFIX")
    health_server_port: int = Field(5000, env="HEALTH_SERVER_PORT")
    redis_host: str = Field(..., env="REDIS_HOSTNAME")
    redis_port: int = Field(6379, env="REDIS_PORT")
    nats_server: str = Field(..., env="NATS_SERVER")
    bruin_base_url: str = Field(..., env="BRUIN_BASE_URL")
    bruin_login_url: str = Field(..., env="BRUIN_LOGIN_URL")
    bruin_client_id: str = Field(..., env="BRUIN_CLIENT_ID")
    bruin_client_secret: str = Field(..., env="BRUIN_CLIENT_SECRET")
    forticloud_base_url: str = Field(..., env="FORTICLOUD_BASE_URL")
    forticloud_account_id: str = Field(..., env="FORTICLOUD_ACCOUNT")
    forticloud_username: str = Field(..., env="FORTICLOUD_USERNAME")
    forticloud_password: str = Field(..., env="FORTICLOUD_PASSWORD")
    ap_consumer_queue: str = "forticloud-monitor.aps"
    ap_consumer_subject: str = "forticloud.aps"
    switch_consumer_queue: str = "forticloud-monitor.switches"
    switch_consumer_subject: str = "forticloud.switches"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def bruin_credentials(self) -> BruinCredentials:
        return BruinCredentials(self.bruin_client_id, self.bruin_client_secret)

    @property
    def forticloud_config(self):
        return {
            "base_url": self.forticloud_base_url,
            "account_id": self.forticloud_account_id,
            "username": self.forticloud_username,
            "password": self.forticloud_password,
        }

    @property
    def ap_consumer_settings(self) -> ConsumerSettings:
        return ConsumerSettings(self.ap_consumer_queue, self.ap_consumer_subject)

    @property
    def switch_consumer_settings(self) -> ConsumerSettings:
        return ConsumerSettings(self.switch_consumer_queue, self.switch_consumer_subject)

    @property
    def nats_settings(self) -> NatsSettings:
        return NatsSettings(servers=[self.nats_server])

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
    def stout_handler(self):
        handler = StdoutHandler()
        formatter = StandardFormatter(environment_name=self.environment_name)
        handler.setFormatter(formatter)
        return handler

    @property
    def papetrail_handler(self):
        handler = PapertrailHandler(host=self.papertrail_host, port=self.papertrail_port)
        formatter = PapertrailFormatter(
            environment_name=self.environment_name,
            papertrail_prefix=self.papertrail_prefix,
        )
        handler.setFormatter(formatter)
        return handler
