from unittest.mock import Mock

from application.rpc.base.rpc_response import RpcResponse, UNKNOWN_STATUS, OK_STATUS


class TestRpcResponse:
    def instance_test(self):
        status = Mock(int)
        body = Mock(dict)

        subject = RpcResponse(status=status, body=body)

        assert subject.status == status
        assert subject.body == body

    def non_dict_responses_are_properly_built_test(self):
        subject = RpcResponse.from_response(None)

        assert subject == RpcResponse(status=UNKNOWN_STATUS, body={})

    def non_numeric_status_responses_are_properly_built_test(self):
        body = Mock(dict)
        subject = RpcResponse.from_response({"status": "non_numeric_status", "body": body})

        assert subject == RpcResponse(status=UNKNOWN_STATUS, body=body)

    def non_dict_bodies_are_properly_built_test(self):
        subject = RpcResponse.from_response({"body": None})

        assert subject == RpcResponse(status=UNKNOWN_STATUS, body={})

    def non_body_responses_are_properly_built_test(self):
        status = 0
        subject = RpcResponse.from_response({"status": status})

        assert subject == RpcResponse(status=status, body={})

    def rpc_responses_are_properly_built_test(self):
        status = 0
        body = Mock(dict)

        subject = RpcResponse.from_response({"status": status, "body": body})

        assert subject == RpcResponse(status=status, body=body)

    def ok_response_are_properly_detected_test(self):
        assert RpcResponse(status=OK_STATUS, body={}).is_ok()

    def ko_response_are_properly_detected_test(self):
        assert not RpcResponse(status=400, body={}).is_ok()
