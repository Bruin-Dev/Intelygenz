# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import application.clients.generated_grpc.public_input_pb2 as public__input__pb2


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


class EntrypointServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetPrediction(self, request, context):
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
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "entrypoint.Entrypoint", rpc_method_handlers
    )
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