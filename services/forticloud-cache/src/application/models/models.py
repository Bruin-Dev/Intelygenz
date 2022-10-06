from pydantic import BaseModel, Field


class Network(BaseModel):
    id: int = Field(alias="oid")


class Switch(BaseModel):
    network_id: int = Field(alias="network")
    serial_number: str = Field(alias="sn")


class AccessPoint(BaseModel):
    serial_number: str = Field(alias="serial")
