import logging

from application.data.email_tagger import prediction_response, save_metrics_response
from application.scenario import get_current_scenario
from application.servers.grpc.email_tagger.email_tagger_pb2 import DESCRIPTOR
from application.servers.grpc.email_tagger.email_tagger_pb2_grpc import (
    EntrypointServicer,
    EntrypointStub,
    add_EntrypointServicer_to_server,
)
from application.servers.grpc.grpc import GrpcServer, GrpcService
from dataclasses import dataclass
from grpc import aio

log = logging.getLogger(__name__)


@dataclass
class EmailTaggerService(GrpcService, EntrypointServicer):
    stub_class = EntrypointStub

    @staticmethod
    def path(method_name: str) -> str:
        return GrpcService.method_path("email-tagger", "Entrypoint", method_name, DESCRIPTOR)

    async def GetPrediction(self, request, context):
        path = EmailTaggerService.path("GetPrediction")
        log.info(f"path={path}")
        response = await get_current_scenario().handle_grpc(
            path=path,
            request=request,
            context=context,
            resend=self.resend_get_prediction,
        )

        log.info(f"path={path} => response={response}")
        return response

    async def resend_get_prediction(self, request, context):
        log.info(f"resend_get_prediction(request={request})")
        return await self.stub().GetPrediction(request) if self.proxy else prediction_response()

    async def SaveMetrics(self, request, context):
        path = EmailTaggerService.path("SaveMetrics")
        log.info(f"path={path}")
        response = await get_current_scenario().handle_grpc(
            path=path,
            request=request,
            context=context,
            resend=self.resend_save_metrics,
        )

        log.info(f"path={path} => response={response}")
        return response

    async def resend_save_metrics(self, request, context):
        log.info(f"resend_save_metrics(request={request})")
        return await self.stub().SaveMetrics(request) if self.proxy else save_metrics_response()


@dataclass
class EmailTaggerServer(GrpcServer):
    async def start(self, port: int):
        log.info(f"Starting GRPC server on port [{port}] ...")
        self.server = aio.server()

        add_EntrypointServicer_to_server(EmailTaggerService(self.proxy), self.server)
        self.server.add_insecure_port(f"[::]:{port}")

        await self.server.start()
        log.info(f"GRPC server started on port [{port}]")
        await self.server.wait_for_termination()

    async def stop(self):
        self.server.stop()
