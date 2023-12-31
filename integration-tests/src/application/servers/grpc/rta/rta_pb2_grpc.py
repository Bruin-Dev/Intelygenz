# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import application.servers.grpc.rta.rta_pb2 as public__input__pb2
import grpc


class EntrypointStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetPrediction = channel.unary_unary(
            "/entrypoint.Entrypoint/GetPrediction",
            request_serializer=public__input__pb2.PredictionRequest.SerializeToString,
            response_deserializer=public__input__pb2.PredictionResponse.FromString,
        )
        self.SaveOutputs = channel.unary_unary(
            "/entrypoint.Entrypoint/SaveOutputs",
            request_serializer=public__input__pb2.SaveOutputsRequest.SerializeToString,
            response_deserializer=public__input__pb2.SaveOutputsResponse.FromString,
        )
        self.SaveCreatedTicketsFeedback = channel.unary_unary(
            "/entrypoint.Entrypoint/SaveCreatedTicketsFeedback",
            request_serializer=public__input__pb2.SaveCreatedTicketsFeedbackRequest.SerializeToString,
            response_deserializer=public__input__pb2.SaveCreatedTicketsFeedbackResponse.FromString,
        )
        self.SaveClosedTicketsFeedback = channel.unary_unary(
            "/entrypoint.Entrypoint/SaveClosedTicketsFeedback",
            request_serializer=public__input__pb2.SaveClosedTicketsFeedbackRequest.SerializeToString,
            response_deserializer=public__input__pb2.SaveClosedTicketsFeedbackResponse.FromString,
        )


class EntrypointServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetPrediction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SaveOutputs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SaveCreatedTicketsFeedback(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SaveClosedTicketsFeedback(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_EntrypointServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetPrediction": grpc.unary_unary_rpc_method_handler(
            servicer.GetPrediction,
            request_deserializer=public__input__pb2.PredictionRequest.FromString,
            response_serializer=public__input__pb2.PredictionResponse.SerializeToString,
        ),
        "SaveOutputs": grpc.unary_unary_rpc_method_handler(
            servicer.SaveOutputs,
            request_deserializer=public__input__pb2.SaveOutputsRequest.FromString,
            response_serializer=public__input__pb2.SaveOutputsResponse.SerializeToString,
        ),
        "SaveCreatedTicketsFeedback": grpc.unary_unary_rpc_method_handler(
            servicer.SaveCreatedTicketsFeedback,
            request_deserializer=public__input__pb2.SaveCreatedTicketsFeedbackRequest.FromString,
            response_serializer=public__input__pb2.SaveCreatedTicketsFeedbackResponse.SerializeToString,
        ),
        "SaveClosedTicketsFeedback": grpc.unary_unary_rpc_method_handler(
            servicer.SaveClosedTicketsFeedback,
            request_deserializer=public__input__pb2.SaveClosedTicketsFeedbackRequest.FromString,
            response_serializer=public__input__pb2.SaveClosedTicketsFeedbackResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("entrypoint.Entrypoint", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Entrypoint(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetPrediction(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/entrypoint.Entrypoint/GetPrediction",
            public__input__pb2.PredictionRequest.SerializeToString,
            public__input__pb2.PredictionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SaveOutputs(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/entrypoint.Entrypoint/SaveOutputs",
            public__input__pb2.SaveOutputsRequest.SerializeToString,
            public__input__pb2.SaveOutputsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SaveCreatedTicketsFeedback(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/entrypoint.Entrypoint/SaveCreatedTicketsFeedback",
            public__input__pb2.SaveCreatedTicketsFeedbackRequest.SerializeToString,
            public__input__pb2.SaveCreatedTicketsFeedbackResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SaveClosedTicketsFeedback(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/entrypoint.Entrypoint/SaveClosedTicketsFeedback",
            public__input__pb2.SaveClosedTicketsFeedbackRequest.SerializeToString,
            public__input__pb2.SaveClosedTicketsFeedbackResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
