from typing import Dict, Optional

from pydantic import BaseModel, validator


class ForticloudResponse(BaseModel):
    status: int
    body: Dict


class APResponseBody(BaseModel):
    connection_state: Optional[str]
    name: Optional[str]
    disc_type: Optional[str]
    serial: Optional[str]

    @validator("*", pre=True)
    def wrong_string_type(cls, v):
        return None if not isinstance(v, str) else v


class SwitchResponseBody(BaseModel):
    status: Optional[str]
    hostname: Optional[str]
    model: Optional[str]
    sn: Optional[str]

    @validator("*", pre=True)
    def wrong_string_type(cls, v):
        return None if not isinstance(v, str) else v
