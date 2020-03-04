from unittest.mock import Mock

from application.repositories.comparison_report_renderer import ComparisonReportRenderer
from config import testconfig


class TestComparisonReportRenderer:

    def instantiation_test(self):
        config = testconfig
        templates_environment = Mock()

        comparison_report_renderer = ComparisonReportRenderer(config, templates_environment)

        assert comparison_report_renderer._config is testconfig
        assert comparison_report_renderer._templates_environment is templates_environment

    def compose_email_object_test(self):
        edges_to_report = [{
            "detection_time": "2019-12-02 10:03:25.412646-05:00",
            "serial_number": "VC123456789",
            "enterprise": "EVIL-CORP",
            "edge_url": "https://mettel.velocloud.net/#!/operator/customer/22/monitor/edge/3208/",
            "outage_causes": ["Edge was OFFLINE", "Link GE1 was DISCONNECTED"]
        }]
        fields = ["Date of detection", "Serial Number", "Company", "Edge URL", "Outage causes"]
        fields_edge = ["detection_time", "serial_number", "enterprise", "edge_url", "outage_causes"]

        email_html = '<html><head>Some head</head><body>Some body</body></html>'

        config = testconfig

        mock_template = Mock()
        mock_template.render = Mock(return_value=email_html)

        templates_environment = Mock()
        templates_environment.get_template = Mock(return_value=mock_template)

        template_renderer = ComparisonReportRenderer(config, templates_environment)

        email_object = template_renderer.compose_email_object(edges_to_report, fields=fields, fields_edge=fields_edge)

        email_object_root_keys = email_object.keys()
        assert 'request_id' in email_object_root_keys
        assert 'email_data' in email_object_root_keys

        email_object_data = email_object['email_data']
        assert 'subject' in email_object_data
        assert 'recipient' in email_object_data
        assert 'html' in email_object_data
        assert 'images' in email_object_data
        assert 'attachments' in email_object_data

        assert email_object_data['html'] == email_html
        assert len(email_object_data['attachments']) == 1
