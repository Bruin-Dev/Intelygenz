class NotifierAction:

    def __new__(cls, logger, event_bus, config, production_action, development_action):

        if config.ENV_CONFIG['environment'] == 'production':
            return production_action(logger, event_bus, config)
        elif config.ENV_CONFIG['environment'] == 'dev':
            return development_action(logger, event_bus, config)
