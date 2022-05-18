from typing import List

from dataclasses import field, dataclass
from pydantic import BaseModel, Field, ValidationError, validator

from application.domain.asset import AssetId, Topic
from application.rpc import Rpc, RpcError

NATS_TOPIC = "bruin.get.asset.topics"


@dataclass
class GetAssetTopicsRpc(Rpc):
    topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, asset_id: AssetId) -> List[Topic]:
        """
        Get the recommended Ticket Call Type and Category for the provided Asset.
        Communication errors will be raised up.
        Unexpected responses will return an empty list.
        :param asset_id: an Asset Id
        :return: a list of recommended Topics
        """
        request, logger = self.start()
        logger.debug(f"__call__(asset_id={asset_id}")

        try:
            request.body = RequestBody.from_asset_id(asset_id)
            response = await self.send(request)

            if response.is_ok():
                try:
                    body = ResponseBody.parse_obj(response.body)
                    topics = [Topic(call_type=item.call_type, category=item.category)
                              for item in body.call_types]

                    logger.debug(f"__call__(): [OK] topics={topics}")
                    return topics

                except ValidationError as e:
                    logger.warning(f"__call__(): [KO] response={response}, validation_error={e}")
                    return []

            else:
                logger.warning(f"__call__(): [KO] response={response}")
                return []

        except Exception as e:
            raise RpcError from e


class RequestBody(BaseModel):
    client_id: int
    service_number: str

    @classmethod
    def from_asset_id(cls, asset_id: AssetId):
        return cls(
            client_id=asset_id.client_id,
            service_number=asset_id.service_number
        )


class ResponseBody(BaseModel):
    call_types: List['ResponseCallType'] = Field(alias="callTypes")

    @validator("call_types", pre=True)
    def only_valid_items(cls, v):
        valid_items = []
        for item in [item for item in v if isinstance(item, dict)]:
            try:
                valid_items.append(ResponseCallType(**item))
            except ValidationError:
                pass

        return valid_items


class ResponseCallType(BaseModel):
    call_type: str = Field(alias="callType")
    category: str


# Resolve forward refs for pydantic
ResponseBody.update_forward_refs()
