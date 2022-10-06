from typing import Dict, Optional

from pydantic import BaseModel, Field, ValidationError, validator


class ForticloudResponse(BaseModel):
    status: int
    body: Dict


class APResponseResult(BaseModel):
    connection_state: Optional[str]
    name: Optional[str]
    disc_type: Optional[str]
    serial: Optional[str]

    @validator("connection_state", "name", "disc_type", "serial", pre=True)
    def validate_strings(cls, v):
        return None if not isinstance(v, str) else v


class APResponseBody(BaseModel):
    result: APResponseResult

    @validator("result", pre=True)
    def validate_result(cls, v):
        try:
            return APResponseResult.parse_obj(v)
        except ValidationError:
            return APResponseResult()


class SwitchResponseConnStatus(BaseModel):
    status: Optional[str]

    @validator("status", pre=True)
    def validate_status(cls, v):
        return None if not isinstance(v, str) else v


class SwitchResponseSystemStatus(BaseModel):
    hostname: Optional[str]
    serial_number: Optional[str]
    model: Optional[str]

    @validator("hostname", "serial_number", "model", pre=True)
    def validate_strings(cls, v):
        return None if not isinstance(v, str) else v


class SwitchResponseSystem(BaseModel):
    status: SwitchResponseSystemStatus = Field(default_factory=SwitchResponseSystemStatus)

    @validator("status", pre=True)
    def validate_status(cls, v):
        try:
            return SwitchResponseSystemStatus.parse_obj(v)
        except ValidationError:
            return SwitchResponseSystemStatus()


class SwitchResponseBody(BaseModel):
    conn_status: SwitchResponseConnStatus = Field(default_factory=SwitchResponseConnStatus)
    system: SwitchResponseSystem = Field(default_factory=SwitchResponseSystem)

    @validator("conn_status", pre=True)
    def validate_conn_status(cls, v):
        try:
            return SwitchResponseConnStatus.parse_obj(v)
        except ValidationError:
            return SwitchResponseConnStatus()

    @validator("system", pre=True)
    def validate_system(cls, v):
        try:
            return SwitchResponseSystem.parse_obj(v)
        except ValidationError:
            return SwitchResponseSystem(status=SwitchResponseSystemStatus())
