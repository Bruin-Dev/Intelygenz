from unittest.mock import Mock

from application.rpc.base.rpc_request import RpcRequest


class TestRpcRequest:
    def instance_test(self):
        request_id = Mock(str)

        subject = RpcRequest(request_id=request_id)

        assert subject.request_id == request_id
