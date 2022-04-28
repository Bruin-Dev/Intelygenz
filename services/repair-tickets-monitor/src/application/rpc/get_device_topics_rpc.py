from typing import List

from dataclasses import dataclass

from application.domain.device import Device
from application.domain.topic import Topic
from application.rpc.base.rpc import Rpc
from application.rpc.base.rpc_logger import RpcLogger
from application.rpc.base.rpc_request import RpcRequest
from application.rpc.base.rpc_response import RpcResponse


@dataclass
class DeviceTopicsRequest(RpcRequest):
    """
    Data structure that represents a service topics request.
    """
    client_id: int
    service_number: str

    @classmethod
    def from_device(cls, request_id: str, device: Device):
        return cls(request_id=request_id, client_id=device.client_id, service_number=device.service_number)


class GetDeviceTopicsRpc(Rpc):
    async def get_topics_for(self, device: Device) -> List[Topic]:
        """
        Gets the topics for the provided device.
        Communication errors will be raised up.
        Unexpected responses will return an empty list.
        :param device:
        :return: a list of topics
        """
        request_id, logger = self.init_request()
        logger.debug(f"run(device={device}")

        request = DeviceTopicsRequest.from_device(request_id, device)
        response = await self.send(request)

        if response.is_ok():
            topics = self.to_topics(response=response, logger=logger)
            logger.debug(f"run(ok): topics={topics}")
            return topics
        else:
            logger.debug(f"run(ko): response={response}")
            return []

    @staticmethod
    def to_topics(response: RpcResponse, logger: RpcLogger) -> List[Topic]:
        """
        Maps a response body to a list of topics.
        Only complete topics (with all its attributes) will be returned.

        :param logger: the logger to be used
        :param response: a dict response
        :return: a list of extracted Topics
        """
        call_type_items = response.body.get("callTypes", [])
        if not isinstance(call_type_items, list):
            logger.debug(f"to_topics(): No callTypes found for body {response.body}")
            return []

        topics = []
        for call_type_item in call_type_items:
            if not isinstance(call_type_item, dict):
                continue

            call_type = call_type_item.get("callType")
            category = call_type_item.get("category")
            if all([call_type, category]):
                topics.append(Topic(call_type=call_type, category=category))
            else:
                logger.debug(f"to_topics(): No topic data found for callType {call_type_item}")

        return topics
