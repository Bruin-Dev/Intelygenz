import logging

from application.data.rta import (
    prediction_response,
    save_closed_ticket_feedback_response,
    save_created_ticket_feedback_response,
    save_outputs_response,
)
from application.scenario import get_current_scenario
from application.servers.grpc.grpc import GrpcServer, GrpcService
from application.servers.grpc.rta.rta_pb2 import DESCRIPTOR
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
        path = self.path("GetPrediction")
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

    async def SaveOutputs(self, request, context):
        path = self.path("SaveOutputs")
        log.info(f"path={path}")
        response = await get_current_scenario().handle_grpc(
            path=path,
            request=request,
            context=context,
            resend=self.resend_save_outputs,
        )

        log.info(f"path={path} => response={response}")
        return response

    async def resend_save_outputs(self, request, context):
        log.info(f"resend_save_outputs(request={request})")
        return await self.stub().SaveOutputs(request) if self.proxy else save_outputs_response()

    async def SaveCreatedTicketsFeedback(self, request, context):
        path = self.path("SaveCreatedTicketsFeedback")
        log.info(f"path={path}")
        response = await get_current_scenario().handle_grpc(
            path=path,
            request=request,
            context=context,
            resend=self.resend_save_closed_tickets_feedback,
        )

        log.info(f"path={path} => response={response}")
        return response

    async def resend_save_created_tickets_feedback(self, request, context):
        log.info(f"resend_save_created_tickets_feedback(request={request})")
        if self.proxy:
            return await self.stub().SaveCreatedTicketsFeedback(request)
        else:
            return save_created_ticket_feedback_response()

    async def SaveClosedTicketsFeedback(self, request, context):
        path = self.path("SaveClosedTicketsFeedback")
        log.info(f"path={path}")
        response = await get_current_scenario().handle_grpc(
            path=path,
            request=request,
            context=context,
            resend=self.resend_save_closed_tickets_feedback,
        )

        log.info(f"path={path} => response={response}")
        return response

    async def resend_save_closed_tickets_feedback(self, request, context):
        log.info(f"resend_save_closed_tickets_feedback(request={request})")
        if self.proxy:
            return await self.stub().SaveClosedTicketsFeedback(request)
        else:
            return save_closed_ticket_feedback_response()


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
