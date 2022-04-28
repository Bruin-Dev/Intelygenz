from dataclasses import dataclass


@dataclass
class RpcRequest:
    """
    Data structure that represents a base request
    """
    request_id: str
