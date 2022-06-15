import logging

from application.scenario import get_current_scenario
from application.servers.grpc.grpc import GrpcServer, GrpcService
from application.servers.grpc.rta.rta_pb2 import DESCRIPTOR, OutputFilterFlags, PredictionResponse, SaveOutputsResponse
from application.servers.grpc.rta.rta_pb2_grpc import (
    EntrypointServicer,
    EntrypointStub,
    add_EntrypointServicer_to_server,
)
from dataclasses import dataclass
from grpc import aio

log = logging.getLogger(__name__)


@dataclass
class RtaService(GrpcService, EntrypointServicer):
    stub_class = EntrypointStub

    @staticmethod
    def path(method_name: str) -> str:
        return GrpcService.method_path("rta", "Entrypoint", method_name, DESCRIPTOR)

    async def GetPrediction(self, request, context):
        log.info(f"path={RtaService.path('GetPrediction')}")
        response = await get_current_scenario().handle_grpc(
            path=self.path("GetPrediction"),
            request=request,
            context=context,
            resend=self.resend_get_prediction,
        )

        log.info(f"path={RtaService.path('GetPrediction')} => response={response}")
        return response

    async def resend_get_prediction(self, request, context):
        log.info(f"resend_get_prediction(request={request})")
        return await self.stub().GetPrediction(request) if self.proxy else default_prediction_response()

    async def SaveOutputs(self, request, context):
        log.info(f"path={RtaService.path('SaveOutputs')}")
        response = await get_current_scenario().handle_grpc(
            path=self.path("SaveOutputs"),
            request=request,
            context=context,
            resend=self.resend_save_outputs,
        )

        log.info(f"path={RtaService.path('SaveOutputs')} => response={response}")
        return response

    async def resend_save_outputs(self, request, context):
        log.info(f"resend_save_outputs(request={request})")
        return await self.stub().SaveOutputs(request) if self.proxy else default_save_outputs_response()


def default_prediction_response() -> PredictionResponse:
    return PredictionResponse(
        potential_service_numbers=["any_service_number"],
        potential_ticket_numbers=["any_ticket_number"],
        predicted_class="",
        filter_flags=OutputFilterFlags(
            tagger_is_below_threshold=False,
            rta_model1_is_below_threshold=False,
            rta_model2_is_below_threshold=False,
            is_filtered=False,
            in_validation_set=False,
        ),
    )


def default_save_outputs_response() -> SaveOutputsResponse:
    return SaveOutputsResponse(success=True)


@dataclass
class RtaServer(GrpcServer):
    async def start(self, port: int):
        log.info(f"Starting GRPC server on port [{port}] ...")
        self.server = aio.server()

        add_EntrypointServicer_to_server(RtaService(self.proxy), self.server)
        self.server.add_insecure_port(f"[::]:{port}")

        await self.server.start()
        log.info(f"GRPC server started on port [{port}]")
        await self.server.wait_for_termination()

    def stop(self):
        self.server.stop()
