from typing import List

from pydantic import BaseModel, Field, ValidationError, validator

from application.domain.device import Device
from application.domain.topic import Topic
from application.rpc.base_rpc import RpcRequest, Rpc, RpcError


class GetDeviceTopicsRpc(Rpc):
    async def __call__(self, device: Device) -> List[Topic]:
        """
        Gets the topics for the provided device.
        Communication errors will be raised up.
        Unexpected responses will return an empty list.
        :param device:
        :return: a list of topics
        """
        request_id, logger = self.start()
        logger.debug(f"run(device={device}")

        try:
            request = DeviceTopicsRequest.from_device(request_id, device)
            response = await self.send(request)

            if response.is_ok():
                body = DeviceTopicsBody.parse_obj(response.body)
                topics = [Topic(
                    call_type=item.call_type,
                    category=item.category
                ) for item in body.call_types]

                logger.debug(f"run(ok): topics={topics}")
                return topics

            else:
                logger.debug(f"run(ko): response={response}")
                return []

        except Exception as e:
            raise RpcError from e


class DeviceTopicsRequest(RpcRequest):
    client_id: int
    service_number: str

    @classmethod
    def from_device(cls, request_id: str, device: Device):
        return cls(request_id=request_id, client_id=device.client_id, service_number=device.service_number)


class DeviceTopicsBody(BaseModel):
    call_types: List['CallType'] = Field(alias="callTypes")

    @validator("call_types", pre=True)
    def only_valid_items(cls, v):
        valid_items = []
        for item in [item for item in v if isinstance(item, dict)]:
            try:
                valid_items.append(CallType(**item))
            except ValidationError:
                pass

        return valid_items


class CallType(BaseModel):
    call_type: str = Field(alias="callType")
    category: str


DeviceTopicsBody.update_forward_refs()
