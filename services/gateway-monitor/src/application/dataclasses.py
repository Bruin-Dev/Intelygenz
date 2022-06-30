from typing import List

from dataclasses import dataclass


@dataclass
class Gateway:
    host: str
    id: int
    tunnel_count: int


@dataclass(init=False)
class GatewayList:
    args: List[Gateway]

    def __init__(self, *args):
        self.args = args


@dataclass
class GatewayPair:
    first_tunnel_count: GatewayList
    second_tunnel_count: GatewayList
