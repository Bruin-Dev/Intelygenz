import jinja2
from unittest.mock import patch

from config import testconfig


class TestTemplateRepository:
    def instantiation_test(self, template_repository):
        assert template_repository._config is testconfig

    def build_email_test(self, template_repository):
        client_id = 1
        subject = 'Test email'

        with patch.object(jinja2, 'FileSystemLoader'):
            result = template_repository._build_email(client_id=client_id, subject=subject, template='test.html',
                                                      template_vars={})

        assert result['email_data']['subject'] == subject
        assert result['email_data']['recipient'] == template_repository._get_recipients(client_id)

    def get_recipients_test(self, template_repository):
        client_id = 1
        result = template_repository._get_recipients(client_id)
        expected = 'mettel.automation@intelygenz.com'
        assert result == expected

        client_id = 9994
        result = template_repository._get_recipients(client_id)
        expected = 'mettel.automation@intelygenz.com, HNOCleaderteam@mettel.net'
        assert result == expected
