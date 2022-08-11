import logging
from dataclasses import dataclass
from typing import Optional, TypeVar

from pydantic import BaseModel, ValidationError

from framework.storage import RedisStorage

M = TypeVar("M", bound=BaseModel)

log = logging.getLogger(__name__)


@dataclass
class ModelStorage(RedisStorage[M]):
    """
    RedisStorage implementation to work with pydantic objects
    """

    def _serialize(self, data: M) -> str:
        log.debug(f"_serialize(data={data})")
        return data.json()

    def _deserialize(self, data: Optional[str]) -> Optional[M]:
        log.debug(f"_deserialize(data={data})")

        if data is None:
            return None

        try:
            return self.data_type.parse_raw(data)
        except ValidationError as e:
            log.warning(f"Error deserializing {data}: {e}")
            return None
