import logging
from typing import Any, Optional

import grpc
from dataclasses import dataclass, field
from google.protobuf.descriptor import FileDescriptor

log = logging.getLogger(__name__)


@dataclass
class GrpcServer:
    proxy: Optional[str] = None
    server: grpc.Server = field(init=False)

    async def start(self, port: int):
        raise NotImplementedError

    def stop(self):
        pass


@dataclass
class GrpcService:
    proxy: Optional[str]
    stub_class: Any = field(init=False)

    @staticmethod
    def method_path(server_name: str, service_name: str, method_name: str, descriptor: FileDescriptor) -> str:
        service_descriptor = descriptor.services_by_name[service_name]
        method_descriptor = service_descriptor.FindMethodByName(method_name)
        return f"/{server_name}.{service_descriptor.name}/{method_descriptor.name}"

    def stub(self):
        if self.proxy:
            proxy_channel = grpc.insecure_channel(self.proxy)
            return self.stub_class(proxy_channel)
        else:
            return None
