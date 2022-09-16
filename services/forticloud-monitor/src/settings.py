from pydantic import BaseSettings, Field


class RedisSettings(BaseSettings):
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
