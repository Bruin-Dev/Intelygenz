from config import testconfig as config
from application.repositories.service_outage_report_template_renderer import ServiceOutageReportTemplateRenderer
from config import testconfig


class TestServiceOutageReportTemplateRenderer:

    def instantiation_test(self):
        test_repo = ServiceOutageReportTemplateRenderer(config)
        assert test_repo._config == config

    def compose_email_object_test(self):
        config = testconfig
        template_renderer = ServiceOutageReportTemplateRenderer(config)
        edges_to_report = [{
            "detection_time": "2019-12-02 10:03:25.412646-05:00",
            "serial_number": "VC123456789",
            "enterprise": "EVIL-CORP",
            "edge_url": "https://mettel.velocloud.net/#!/operator/customer/22/monitor/edge/3208/",
            "outage_causes": ["Edge was OFFLINE", "Link GE1 was DISCONNECTED"]
        }]
        fields = ["Date of detection", "Serial Number", "Company", "Edge URL", "Outage causes"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "edge_url", "outage_causes"]
        email = template_renderer.compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)

        assert 'Service Outage Report' in email["email_data"]["subject"]
        assert config.MONITOR_CONFIG["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_table_fields_and_values_check_test(self):
        config = testconfig
        template_renderer = ServiceOutageReportTemplateRenderer(config)
        edges_to_report = [{
            "detection_time": "2019-12-02 10:03:25.412646-05:00",
            "serial_number": "VC123456789",
            "enterprise": "EVIL-CORP",
            "edge_url": "https://mettel.velocloud.net/#!/operator/customer/22/monitor/edge/3208/",
            "outage_causes": ["Edge was OFFLINE", "Link GE1 was DISCONNECTED"]
        }]
        fields = ["Date of detection", "Serial Number", "Company", "Edge URL", "Outage causes"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "edge_url", "outage_causes"]
        email = template_renderer.compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)

        assert all(f"{i}</th>" in email["email_data"]["html"] for i in fields) is True
        assert all((f"{ii}</td >" in email["email_data"]["html"] for ii in i) for i in edges_to_report) is True
