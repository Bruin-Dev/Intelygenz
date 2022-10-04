from typing import Optional

from pydantic import BaseModel, validator


class ApData(BaseModel):
    name: Optional[str] = None
    disc_type: Optional[str] = None
    serial: Optional[str] = None

    @validator("*", pre=True)
    def wrong_string_type(cls, v):
        return None if not isinstance(v, str) else v


class SwitchData(BaseModel):
    hostname: Optional[str] = None
    model: Optional[str] = None
    sn: Optional[str] = None

    @validator("*", pre=True)
    def wrong_string_type(cls, v):
        return None if not isinstance(v, str) else v
