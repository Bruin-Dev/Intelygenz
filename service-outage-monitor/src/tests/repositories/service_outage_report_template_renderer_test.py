from unittest.mock import Mock
from config import testconfig as config
from application.repositories.service_outage_report_template_renderer import ServiceOutageReportTemplateRenderer
from asynctest import CoroutineMock
import base64
from config import testconfig
import subprocess


class TestServiceOutageReportTemplateRenderer:

    def instantiation_test(self):
        test_repo = ServiceOutageReportTemplateRenderer(config)
        assert test_repo._config == config

    def compose_email_object_test(self):
        config = testconfig
        template_renderer = ServiceOutageReportTemplateRenderer(config)
        edges_to_report = [{
            "detection_time": "timestamp",
            "serial_number": "safasfasdf",
            "enterprise": "ajsdkfjhsda",
            "links": "http://asdasfsdf.es - http://asdlkjfhasdlkjfhweq.com - http://asdfsdf.com",
            "tickets": "No"
        }]
        fields = ["Date of detection", "Serial Number", "Company", "LINKS", "Has ticket created?"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "links"]
        email = template_renderer._compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)
        template_renderer._remove_csv_file()

        assert 'Service Outage Report' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_table_fields_and_values_check_test(self):
        config = testconfig
        template_renderer = ServiceOutageReportTemplateRenderer(config)
        edges_to_report = [{
            "detection_time": "timestamp",
            "serial_number": "safasfasdf",
            "enterprise": "ajsdkfjhsda",
            "links": "http://asdasfsdf.es - http://asdlkjfhasdlkjfhweq.com - http://asdfsdf.com",
            "tickets": "No"
        }]
        fields = ["Date of detection", "Serial Number", "Company", "LINKS", "Has ticket created?"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "links", "tickets"]
        email = template_renderer._compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)
        template_renderer._remove_csv_file()

        assert all(f"{i}</th>" in email["email_data"]["html"] for i in fields) is True
        assert all((f"{ii}</td >" in email["email_data"]["html"] for ii in i) for i in edges_to_report) is True

    def compose_email_csv_generated_and_removed_test(self):
        config = testconfig
        template_renderer = ServiceOutageReportTemplateRenderer(config)
        edges_to_report = [{
            "detection_time": "timestamp",
            "serial_number": "safasfasdf",
            "enterprise": "ajsdkfjhsda",
            "links": "http://asdasfsdf.es - http://asdlkjfhasdlkjfhweq.com - http://asdfsdf.com",
            "tickets": "No"
        }]
        fields = ["Date of detection", "Serial Number", "Company", "LINKS", "Has ticket created?"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "links", "tickets"]
        email = template_renderer._compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)
        template_renderer._remove_csv_file()
        a = subprocess.check_output(["find", "-name", "*.csv"]).decode()
        assert "report_mail_template" not in a
