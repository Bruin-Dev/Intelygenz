from collections import OrderedDict
from unittest.mock import Mock

from dateutil.parser import parse

from application.repositories.triage_report_renderer import TriageReportRenderer
from config import testconfig


class TestTriageReportRenderer:

    def instantiation_test(self):
        config = testconfig
        templates_environment = Mock()

        triage_report_renderer = TriageReportRenderer(config, templates_environment)

        assert triage_report_renderer._config is testconfig
        assert triage_report_renderer._templates_environment is templates_environment

    def compose_email_object_test(self):
        payload = OrderedDict({
            'Orchestrator Instance': 'some-host',
            'Edge Name': 'Travis Touchdown',
            'Links': {
                'Edge': 'https://some-host/#!/operator/customer/100/monitor/edge/200/',
                'QoE': 'https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/',
                'Transport': 'https://some-host/#!/operator/customer/100/monitor/edge/200/links/',
                'Events': 'https://some-host/#!/operator/customer/100/monitor/events/',
            },
            'Edge Status': 'OFFLINE',
            'Serial': 'VC1234567',
            'Interface GE1': '',
            'Interface GE1 Label': 'Solid Snake',
            'Interface GE1 Status': 'DISCONNECTED',
            'Interface GE2': '',
            'Interface GE2 Label': None,
            'Interface GE2 Status': 'Interface GE2 not available',
            'Interface INTERNET3': '',
            'Interface INTERNET3 Label': 'Otacon',
            'Interface INTERNET3 Status': 'STABLE',
            'Interface GE10': '',
            'Interface GE10 Label': 'Big Boss',
            'Interface GE10 Status': 'STABLE',
            'Last Edge Online': parse('2019-08-01 10:40:00+00:00'),
            'Last Edge Offline': parse('2019-08-01 11:40:00+00:00'),
            'Last GE1 Interface Online': parse('2019-07-30 02:40:00+00:00'),
            'Last GE1 Interface Offline': parse('2019-07-30 01:40:00+00:00'),
            'Last GE2 Interface Online': parse('2019-07-01 07:40:00+00:00'),
            'Last GE2 Interface Offline': parse('2019-07-30 00:40:00+00:00'),
            'Last INTERNET3 Interface Online': parse('2019-08-01 09:40:00+00:00'),
            'Last INTERNET3 Interface Offline': None,
            'Last GE10 Interface Online': None,
            'Last GE10 Interface Offline': None,
        })

        email_html = '<html><head>Some head</head><body>Some body</body></html>'

        config = testconfig

        mock_template = Mock()
        mock_template.render = Mock(return_value=email_html)

        templates_environment = Mock()
        templates_environment.get_template = Mock(return_value=mock_template)

        triage_report_renderer = TriageReportRenderer(config, templates_environment)

        email_object = triage_report_renderer.compose_email_object(payload)

        email_object_root_keys = email_object.keys()
        assert 'request_id' in email_object_root_keys
        assert 'email_data' in email_object_root_keys

        email_object_data = email_object['email_data']
        assert 'subject' in email_object_data
        assert 'recipient' in email_object_data
        assert 'html' in email_object_data
        assert 'images' in email_object_data

        assert email_object_data['html'] == email_html
