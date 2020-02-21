import base64

from collections import OrderedDict

from application.repositories.triage_report_renderer import TriageReportRenderer
from config import testconfig


class TestTriageReportRenderer:

    def instantiation_test(self):
        test_repo = TriageReportRenderer(testconfig)
        assert test_repo._config == testconfig

    def compose_email_object_test(self):
        test_repo = TriageReportRenderer(testconfig)
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Company Events URL"] = 'test.com',
        ticket_dict['Events URL'] = 'event.com'
        email = test_repo._ticket_object_to_email_obj(ticket_dict)
        assert email is not None
        assert isinstance(email, dict) is True

    def compose_email_object_html_elements_test(self):
        base = "src/templates/triage/images/{}"
        kwargs = dict(logo="logo.png",
                      header="header.jpg")
        test_repo = TriageReportRenderer(testconfig)
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Company Events URL"] = 'test.com',
        ticket_dict['Events URL'] = 'event.com'
        email = test_repo._ticket_object_to_email_obj(ticket_dict)
        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')

    def ticket_object_to_email_obj_test(self):
        config = testconfig
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Company Events URL"] = 'test.com',
        ticket_dict['Events URL'] = 'event.com'
        template_renderer = TriageReportRenderer(config)
        email = template_renderer._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def ticket_object_to_email_obj_test(self):
        config = testconfig
        template_renderer = TriageReportRenderer(config)
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        ticket_dict["Company Events URL"] = 'test.com',
        ticket_dict['Events URL'] = 'event.com'
        email = template_renderer._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def ticket_object_to_email_obj_no_events_test(self):
        config = testconfig
        template_renderer = TriageReportRenderer(config)
        ticket_dict = OrderedDict()
        ticket_dict['EdgeName'] = 'Test'
        ticket_dict['Edge Status'] = 'ok'
        email = template_renderer._ticket_object_to_email_obj(ticket_dict)

        assert 'Service outage triage' in email["email_data"]["subject"]
        assert config.TRIAGE_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
