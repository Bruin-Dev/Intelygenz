from unittest.mock import Mock
from config import testconfig as config
from application.repositories.edge_repository_template_renderer import EdgeRepositoryTemplateRenderer
from asynctest import CoroutineMock
import base64
from config import testconfig


class TestTemplateRenderer:

    def instantiation_test(self):
        mock_service_id = Mock()
        test_repo = EdgeRepositoryTemplateRenderer(config)
        assert test_repo._config == config

    def compose_email_object_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        template_renderer = EdgeRepositoryTemplateRenderer(config)
        edges_to_report = [
            {"edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
             "enterprise": "Fake Corp"}]
        email = template_renderer._compose_email_object(edges_to_report)

        assert 'Last contact edges' in email["email_data"]["subject"]
        assert config["last_contact"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        base = "src/templates/images/{}"
        kwargs = dict(template="last_contact.html",
                      logo="logo.png",
                      header="header.jpg",
                      csv="last_contact.csv")
        test_repo = EdgeRepositoryTemplateRenderer(config.ALERTS_CONFIG)
        edges_to_report = [
            dict(edge={"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
                 enterprise="Fake Corp")]
        email = test_repo._compose_email_object(edges_to_report, **kwargs)
        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["attachments"][0]["data"] == base64.b64encode(open(kwargs["csv"], 'rb')
                                                                                 .read()).decode('utf-8')

    def compose_email_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        template_renderer = EdgeRepositoryTemplateRenderer(config)

        edges_to_report = [
            {"edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
             "enterprise": "Fake Corp"}]
        email = template_renderer._compose_email_object(edges_to_report)
        assert 'Last contact edges' in email["email_data"]["subject"]
        assert config["last_contact"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
