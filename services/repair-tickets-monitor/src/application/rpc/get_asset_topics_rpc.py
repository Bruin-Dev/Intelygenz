import logging
from dataclasses import dataclass, field
from typing import List

from application.domain.asset import AssetId, Topic
from application.rpc import Rpc, RpcFailedError, RpcRequest
from pydantic import BaseModel, Field, ValidationError, validator

log = logging.getLogger(__name__)

NATS_TOPIC = "bruin.get.asset.topics"


@dataclass
class GetAssetTopicsRpc(Rpc):
    _topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, asset_id: AssetId) -> List[Topic]:
        """
        Get the recommended Ticket Call Type and Category for the provided Asset.
        Proxied service: GET /api/Ticket/topics
        :raise RpcFailedError: if the response cannot be parsed correctly.
        :param asset_id: an Asset Id
        :return: a list of recommended Topics
        """
        log.debug(f"__call__(asset_id={asset_id})")

        request = RpcRequest(body=RequestBody(client_id=asset_id.client_id, service_number=asset_id.service_number))
        response = await self.send(request)

        try:
            body = ResponseBody.parse_obj(response.body)
            topics = [Topic(call_type=item.call_type, category=item.category) for item in body.call_types]

            log.debug(f"__call__(): topics={topics}, response={response.body}")
            return topics

        except ValidationError as error:
            raise RpcFailedError(request=request, response=response) from error


class ResponseCallType(BaseModel):
    call_type: str = Field(alias="callType")
    category: str


class RequestBody(BaseModel):
    client_id: str
    service_number: str


class ResponseBody(BaseModel):
    call_types: List[ResponseCallType] = Field(alias="callTypes")

    @validator("call_types", pre=True)
    def only_valid_items(cls, v):
        valid_items = []
        for item in [item for item in v if isinstance(item, dict)]:
            try:
                valid_items.append(ResponseCallType(**item))
            except ValidationError:
                pass

        return valid_items
