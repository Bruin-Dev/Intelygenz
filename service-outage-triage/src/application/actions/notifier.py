from application.actions.production import ProductionAction
from application.actions.development import DevelopmentAction


class NotifierAction:

    def __new__(cls, event_bus, config):

        if config.TRIAGE_CONFIG['environment'] == 'production':
            return ProductionAction(event_bus, config)
        elif config.TRIAGE_CONFIG['environment'] == 'dev':
            return DevelopmentAction(event_bus, config)
