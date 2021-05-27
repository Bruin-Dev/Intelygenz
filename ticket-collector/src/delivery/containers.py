"""Delivery containers module."""
from dependency_injector import containers, providers
from .tasks.server import ITasksServer, TasksServer


class Delivery(containers.DeclarativeContainer):
    adapters = providers.DependenciesContainer()
    use_cases = providers.DependenciesContainer()

    tasks_server: ITasksServer = providers.Singleton(
        TasksServer,
        config=adapters.config,
        logger=adapters.logger,
        use_cases=use_cases
    )
