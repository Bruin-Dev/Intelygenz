from pydantic import BaseSettings, Field


class LoggingConfiguration(BaseSettings):
    level: str = Field("DEBUG", env="LOG_LEVEL")


class Configuration(BaseSettings):
    environment: str = Field(..., env="ENVIRONMENT_NAME")
    logging = LoggingConfiguration()


config = Configuration()
