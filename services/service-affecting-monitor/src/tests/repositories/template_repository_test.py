from unittest.mock import patch

import jinja2
from config import testconfig


class TestTemplateRepository:
    def instantiation_test(self, template_repository):
        assert template_repository._config is testconfig

    def build_email_test(self, template_repository):
        subject = "Test email"
        recipients = ["a@mettel.com", "b@mettel.com"]

        with patch.object(jinja2, "FileSystemLoader"):
            result = template_repository._build_email(
                subject=subject, recipients=recipients, template="test.html", template_vars={}
            )

        assert result["email_data"]["subject"] == subject
        assert result["email_data"]["recipient"] == "a@mettel.com, b@mettel.com"
