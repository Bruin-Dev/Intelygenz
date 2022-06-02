"""Delivery containers module."""
from delivery.http.server import FlaskServer, IHTTPServer
from dependency_injector import containers, providers


class Delivery(containers.DeclarativeContainer):
    adapters = providers.DependenciesContainer()
    use_cases = providers.DependenciesContainer()

    http_server: IHTTPServer = providers.Singleton(
        FlaskServer, config=adapters.config, logger=adapters.logger, adapters=adapters, use_cases=use_cases
    )
