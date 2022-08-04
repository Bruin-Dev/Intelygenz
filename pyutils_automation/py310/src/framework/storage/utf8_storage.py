import logging
from typing import Optional, Type

from dataclasses import dataclass
from framework.storage import RedisStorage

log = logging.getLogger(__name__)


@dataclass
class Utf8Storage(RedisStorage[bytes]):
    """
    RedisStorage implementation to work with bytes objects
    """

    data_type: Type = bytes

    def _serialize(self, data: bytes) -> str:
        log.debug(f"_serialize(data={data})")
        return data.decode("utf-8")

    def _deserialize(self, data: Optional[str]) -> Optional[bytes]:
        log.debug(f"_deserialize(data={data})")
        return None if data is None else data.encode("utf-8")
