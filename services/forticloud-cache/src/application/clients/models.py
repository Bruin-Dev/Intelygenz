from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# Networks
class Ssid(BaseModel):
    id: Optional[int] = Field(alias="ssidOid")
    name: Optional[str] = Field(alias="ssid")
    user_count: Optional[int] = Field(alias="userCount")


class Network(BaseModel):
    id: int = Field(alias="oid")
    name: Optional[str]
    timezone: Optional[str]
    total_aps: Optional[int] = Field(alias="totalap")
    online_access_points: Optional[int] = Field(alias="onlineap")
    offline_access_points: Optional[int] = Field(alias="offlineap")
    SSIDs: Optional[list[Ssid]] = Field(alias="ssidInfo")


# Switches
class Ipv4Config(BaseModel):
    address: Optional[str]
    mask: Optional[str]


class Ipv6Config(BaseModel):
    address: Optional[str]
    length: Optional[str]


class SpeedStats(BaseModel):
    unit: Optional[str]
    value: Optional[int]


class TransferStats(BaseModel):
    rx_bytes: Optional[int] = Field(alias="rx-bytes")
    rx_packets: Optional[int] = Field(alias="rx-packets")
    tx_bytes: Optional[int] = Field(alias="tx-bytes")
    tx_packets: Optional[int] = Field(alias="tx-packets")


class Interface(BaseModel):
    duplex: Optional[str]
    ipv4_config: Optional[Ipv4Config] = Field(alias="ipv4")
    ipv6_config: Optional[Ipv6Config] = Field(alias="ipv6")
    mode: Optional[str]
    name: Optional[str]
    speed: Optional[SpeedStats]
    status: Optional[str]
    transfer_stats: Optional[TransferStats] = Field(alias="stats")


class PhysicalInterface(BaseModel):
    interfaces: Optional[list[Interface]] = Field(alias="interface")
    title: Optional[str]


class Switch(BaseModel):
    auto_network_enable: Optional[bool]
    bios: Optional[str]
    bios_upgrade_alert: Optional[Any]
    config: Optional[dict[str, Any]]
    connect_time: Optional[str] = Field(alias="connectTime")
    created_at: Optional[str]
    deactivation_time: Optional[Any] = Field(alias="deactive_time")
    firmware_status: Optional[str]
    grace_period_days: Optional[int]
    hostname: Optional[str]
    ip: Optional[str]
    is_deactivated: Optional[bool] = Field(alias="deactive")
    last_seen: Optional[str]
    licensed: Optional[bool]
    license_data: Optional[list[Any]]
    license_status: Optional[Literal["No License", "Active"]] = Field(alias="license")
    local_interface: Optional[str]
    local_ip: Optional[str]
    mac: Optional[str]
    model: Optional[str]
    network_id: int = Field(alias="network")
    nvp: Optional[dict[str, Any]]
    physical_interfaces: Optional[list[PhysicalInterface]] = Field(alias="physical_interface")
    poe_warning: Optional[bool]
    registration_date: Optional[str]
    rma_comment: Optional[str]
    rma_complete: Optional[bool]
    rma_contact_number: Optional[str]
    rma_date: Optional[str]
    rma_from_serial_number: Optional[str]
    rma_to_serial_number: Optional[str]
    serial_number: str = Field(alias="sn")
    status: Literal["connected", "offline", "online"]
    system_part: Optional[str] = Field(alias="systemPart")
    tags: Optional[list[Any]]
    upgrade_schedule: Optional[Any]
    version: Optional[str]


# Access Points (APs)
class AccessPoint(BaseModel):
    serial_number: str = Field(alias="serial")
    active_clients: Optional[int] = Field(alias="clients")
    allow_access_code: Optional[int] = Field(alias="allowAccessCode")
    board_mac: Optional[str]
    connecting_from: Optional[str]
    connection_state: Literal["connected", "Connected", "disconnected", "Disconnected"]
    console_login: Optional[str] = Field(alias="ap_console_login")
    cpu_load: Optional[int]
    data_chan_sec: Optional[str]
    data_chan_connecting_from: Optional[str] = Field(alias="datachan_connecting_from")
    overriden_profile_settings: Optional[dict[str, str]] = Field(alias="apProfileOverride")
    profile_id: Optional[int] = Field(alias="ap_profile")
    profile_name: Optional[str] = Field(alias="ap_profile_name")
