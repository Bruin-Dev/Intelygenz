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


@dataclass
class GrpcService:
    """
    A GRPC Service wrapper to provide shorthand methods to any GRPC service implementation
    """

    proxy: Optional[str]
    stub_class: Any = field(init=False)

    @staticmethod
    def method_path(server_name: str, service_name: str, method_name: str, descriptor: FileDescriptor) -> str:
        """
        Builds an opinionated service method path based on a GRPC descriptor
        :param server_name: the name of the server
        :param service_name: the name of the service
        :param method_name: the name of the method
        :param descriptor: the GRPC descriptor to look for the actual GRPC names
        :return: a service method path
        """
        service_descriptor = descriptor.services_by_name[service_name]
        method_descriptor = service_descriptor.FindMethodByName(method_name)
        return f"/{server_name}.{service_descriptor.name}/{method_descriptor.name}"

    def stub(self):
        """
        Builds an insecure stub to the proxied host if any was defined
        :return:
        """
        if self.proxy:
            proxy_channel = grpc.insecure_channel(self.proxy)
            return self.stub_class(proxy_channel)
        else:
            return None
