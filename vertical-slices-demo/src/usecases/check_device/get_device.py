import logging
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ValidationError

from clients.http_client import HttpClient, HttpRequest
from shared.errors import UnexpectedResponseError, UnexpectedStatusError

from .device import Device, DeviceId, DeviceStatus

log = logging.getLogger(__name__)


@dataclass
class GetDevice:
    http_client: HttpClient

    async def __call__(self, device_id: DeviceId) -> Device:  # pragma: no cover
        log.debug(f"(device_id={device_id}")
        request = GetDeviceRequest(RequestBody.build_for(device_id).dict())
        response = await self.http_client.send(request)
        log.debug(f"http_client.send({request})={response}")
        if not response.is_ok:
            raise UnexpectedStatusError(response.status)

        try:
            response_body = ResponseBody.parse_raw(response.body)
        except ValidationError as e:
            raise UnexpectedResponseError from e

        return Device(id=device_id, status=DeviceStatus[response_body.status])


@dataclass
class GetDeviceRequest(HttpRequest):
    method: str = "GET"
    path: str = "/api/Device"


class RequestBody(BaseModel):
    device_id: int
    network_id: int

    @classmethod
    def build_for(cls, device_id: DeviceId):
        return cls(device_id=device_id.id, network_id=device_id.network_id)


class ResponseBody(BaseModel):
    status: Literal["ONLINE", "OFFLINE"]
