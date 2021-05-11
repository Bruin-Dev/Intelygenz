import base64

from application.repositories.template_management import TemplateRenderer
from config import testconfig


class TestTemplateRenderer:

    def instantiation_test(self):
        config = testconfig
        test_repo = TemplateRenderer(config)
        assert test_repo._config == config

    def ticket_object_to_email_obj_test(self):
        template_renderer = TemplateRenderer(testconfig)
        client_id = 83109
        client_name = 'Benchmark Senior Living - Network'
        test_dict = [
            {
                'customer': {
                    'client_id': client_id, 'client_name': client_name
                },
                'location': {
                    'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714',
                    'country': 'USA'
                },
                'serial_number': 'VC05200085762',
                'number_of_tickets': 4,
                'bruin_tickets_id': [
                    5081250, 5075176, 5074441, 5073652
                ],
                'interfaces': [
                    'GE1', 'GE2'
                ],
                'trouble': 'Bandwidth Over Utilization'
            },
            {
                'customer': {
                    'client_id': client_id, 'client_name': client_name
                },
                'location': {
                    'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714',
                    'country': 'USA'
                },
                'serial_number': 'VC05200085762',
                'number_of_tickets': 4,
                'bruin_tickets_id': [
                    5081250, 5075176, 5074441, 5073652
                ],
                'interfaces': 'GE1',
                'trouble': 'Jitter'
            }
        ]

        email = template_renderer.compose_email_report_object(client_name=client_name,
                                                              client_id=client_id,
                                                              report_items=test_dict)

        assert 'Reoccurring Service Affecting Trouble ' in email["email_data"]["subject"]
        assert client_name in email["email_data"]["subject"]
        assert template_renderer._config.MONITOR_REPORT_CONFIG['report_config_by_trouble']['default']["recipient"][
                   0] in \
               email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]

    def compose_email_object_html_elements_test(self):
        base = "src/templates/images/{}"
        kwargs = dict(logo="logo.png",
                      header="header.jpg")
        template_renderer = TemplateRenderer(testconfig)
        client_id = 83109
        client_name = 'Benchmark Senior Living - Network'
        test_dict = [
            {
                'customer': {
                    'client_id': client_id, 'client_name': client_name
                },
                'location': {
                    'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714',
                    'country': 'USA'
                },
                'serial_number': 'VC05200085762',
                'number_of_tickets': 4,
                'bruin_tickets_id': [
                    5081250, 5075176, 5074441, 5073652
                ],
                'interfaces': [
                    'GE1', 'GE2'
                ],
                'trouble': 'Bandwidth Over Utilization'
            },
            {
                'customer': {
                    'client_id': client_id, 'client_name': client_name
                },
                'location': {
                    'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714',
                    'country': 'USA'
                },
                'serial_number': 'VC05200085762',
                'number_of_tickets': 4,
                'bruin_tickets_id': [
                    5081250, 5075176, 5074441, 5073652
                ],
                'interfaces': 'GE1',
                'trouble': 'Jitter'
            }
        ]

        email = template_renderer.compose_email_report_object(client_name=client_name,
                                                              client_id=client_id,
                                                              report_items=test_dict)

        assert email["email_data"]["images"][0]["data"] == base64.b64encode(open(base.format(kwargs["logo"]), 'rb')
                                                                            .read()).decode('utf-8')
        assert email["email_data"]["images"][1]["data"] == base64.b64encode(open(base.format(kwargs["header"]), 'rb')
                                                                            .read()).decode('utf-8')

    def compose_email_object_empty_html_test(self):
        template_renderer = TemplateRenderer(testconfig)
        client_name = 'Benchmark Senior Living - Network'
        client_id = 83109
        test_dict = []

        email = template_renderer.compose_email_report_object(client_name=client_name,
                                                              client_id=client_id,
                                                              report_items=test_dict)

        assert email == []
