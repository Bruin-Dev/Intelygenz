import logging

from application.scenario import get_current_scenario
from application.servers.grpc.email_tagger.email_tagger_pb2 import DESCRIPTOR, PredictionResponse
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
        log.info(f"path={EmailTaggerService.path('GetPrediction')}")
        response = await get_current_scenario().handle_grpc(
            path=self.path("GetPrediction"),
            request=request,
            context=context,
            resend=self.resend_get_prediction,
        )

        log.info(f"path={EmailTaggerService.path('GetPrediction')} => response={response}")
        return response

    async def resend_get_prediction(self, request, context):
        log.info(f"resend_get_prediction(request={request})")
        return await self.stub().GetPrediction(request) if self.proxy else default_prediction_response()


def default_prediction_response() -> PredictionResponse:
    return PredictionResponse(
        success=True,
        message="any_message",
        email_id="any_email_id",
        prediction=[PredictionResponse.Prediction(tag_id=1, probability=0.9)],
    )


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
