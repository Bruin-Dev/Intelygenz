from unittest.mock import Mock

from application.domain.device import Device


class TestDevice:
    def instance_test(self):
        service_number, client_id = Mock(str), Mock(int)

        subject = Device(service_number=service_number, client_id=client_id)

        assert subject.service_number == service_number
        assert subject.client_id == client_id
        assert subject.allowed_topics == []
