import base64
from unittest.mock import Mock

import pandas as pd
from application.repositories.template_management import TemplateRenderer
from asynctest import CoroutineMock
from config import testconfig
from config import testconfig as config


class TestTemplateRenderer:
    def instantiation_test(self):
        test_repo = TemplateRenderer(config)
        assert test_repo._config == config

    def compose_email_object_test(self):
        config = testconfig.REPORT_CONFIG
        template_renderer = TemplateRenderer(config)
        edges_to_report = [
            {
                "edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
                "enterprise": "Fake Corp",
            }
        ]
        email = template_renderer.compose_email_object(edges_to_report)

        assert "Last contact edges" in email["email_data"]["subject"]
        assert config["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        base = "src/templates/images/{}"
        kwargs = dict(template="last_contact.html", logo="logo.png", header="header.jpg")
        test_repo = TemplateRenderer(config.REPORT_CONFIG)
        edges_to_report = [
            dict(
                edge={"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"}, enterprise="Fake Corp"
            )
        ]
        edges_dataframe = pd.DataFrame(edges_to_report)
        file_csv = edges_dataframe.to_csv(index=False)
        file_csv = base64.b64encode(file_csv.encode("utf-8"))
        email = test_repo.compose_email_object(edges_to_report, **kwargs)

        assert email["email_data"]["images"][0]["data"] == base64.b64encode(
            open(base.format(kwargs["logo"]), "rb").read()
        ).decode("utf-8")
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(
            open(base.format(kwargs["header"]), "rb").read()
        ).decode("utf-8")
        assert email["email_data"]["attachments"][0]["data"] == file_csv.decode("utf-8")

    def compose_email_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        config = testconfig.REPORT_CONFIG
        template_renderer = TemplateRenderer(config)

        edges_to_report = [
            {
                "edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
                "enterprise": "Fake Corp",
            }
        ]
        email = template_renderer.compose_email_object(edges_to_report)

        assert "Last contact edges" in email["email_data"]["subject"]
        assert config["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
