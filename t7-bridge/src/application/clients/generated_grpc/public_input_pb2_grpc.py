# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from application.clients.generated_grpc import public_input_pb2 as public__input__pb2


class EntrypointStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Prediction = channel.unary_unary(
            '/entrypoint.Entrypoint/Prediction',
            request_serializer=public__input__pb2.PredictionRequest.SerializeToString,
            response_deserializer=public__input__pb2.PredictionResponse.FromString,
        )
        self.SaveMetrics = channel.unary_unary(
            '/entrypoint.Entrypoint/SaveMetrics',
            request_serializer=public__input__pb2.SaveMetricsRequest.SerializeToString,
            response_deserializer=public__input__pb2.SaveMetricsResponse.FromString,
        )


class EntrypointServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Prediction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SaveMetrics(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EntrypointServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Prediction': grpc.unary_unary_rpc_method_handler(
            servicer.Prediction,
            request_deserializer=public__input__pb2.PredictionRequest.FromString,
            response_serializer=public__input__pb2.PredictionResponse.SerializeToString,
        ),
        'SaveMetrics': grpc.unary_unary_rpc_method_handler(
            servicer.SaveMetrics,
            request_deserializer=public__input__pb2.SaveMetricsRequest.FromString,
            response_serializer=public__input__pb2.SaveMetricsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'entrypoint.Entrypoint', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Entrypoint(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Prediction(request,
                   target,
                   options=(),
                   channel_credentials=None,
                   call_credentials=None,
                   insecure=False,
                   compression=None,
                   wait_for_ready=None,
                   timeout=None,
                   metadata=None):
        return grpc.experimental.unary_unary(request, target, '/entrypoint.Entrypoint/Prediction',
                                             public__input__pb2.PredictionRequest.SerializeToString,
                                             public__input__pb2.PredictionResponse.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SaveMetrics(request,
                    target,
                    options=(),
                    channel_credentials=None,
                    call_credentials=None,
                    insecure=False,
                    compression=None,
                    wait_for_ready=None,
                    timeout=None,
                    metadata=None):
        return grpc.experimental.unary_unary(request, target, '/entrypoint.Entrypoint/SaveMetrics',
                                             public__input__pb2.SaveMetricsRequest.SerializeToString,
                                             public__input__pb2.SaveMetricsResponse.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
