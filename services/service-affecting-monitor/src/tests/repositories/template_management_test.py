from config import testconfig


class TestTemplateRenderer:
    def instantiation_test(self, template_renderer):
        assert template_renderer._config is testconfig
