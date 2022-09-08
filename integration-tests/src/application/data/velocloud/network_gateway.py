from pydantic import BaseModel


class NetworkGateway(BaseModel):
    id: str = hash("any_gateway_id")
    name: str = "any_gateway_name"
    gatewayState: str = "Online"
