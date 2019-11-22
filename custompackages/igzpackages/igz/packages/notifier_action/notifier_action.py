class NotifierAction:

    def __new__(cls, logger, event_bus, config, template_renderer, production_action, development_action):

        if config.ENV_CONFIG['environment'] == 'production':
            return production_action(logger, event_bus, template_renderer, config)
        elif config.ENV_CONFIG['environment'] == 'dev':
            return development_action(logger, event_bus, template_renderer, config)
