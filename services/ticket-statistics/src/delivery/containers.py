"""Delivery containers module."""
from dependency_injector import containers, providers
from delivery.http.server import IHTTPServer, FlaskServer


class Delivery(containers.DeclarativeContainer):
    adapters = providers.DependenciesContainer()
    use_cases = providers.DependenciesContainer()

    http_server: IHTTPServer = providers.Singleton(
        FlaskServer,
        config=adapters.config,
        logger=adapters.logger,
        use_cases=use_cases
    )
