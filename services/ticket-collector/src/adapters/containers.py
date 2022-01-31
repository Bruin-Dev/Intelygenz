"""Adapters containers module."""
from dependency_injector import containers, providers

from .repositories.bruin.repo import BruinRepository
from .repositories.tickets.repo import TicketsRepository
from .config.settings import get_config
from .db.mongodb import IDB, MongoDB
from .logger.logger import get_logger


class Adapters(containers.DeclarativeContainer):
    config = providers.Singleton(get_config)
    logger = providers.Singleton(get_logger)
    database: IDB = providers.Singleton(MongoDB, config=config, logger=logger)

    # Repositories
    bruin_repository: BruinRepository = providers.Singleton(
        BruinRepository,
        config=config,
        logger=logger,
    )
    tickets_repository: TicketsRepository = providers.Singleton(
        TicketsRepository,
        database=database,
        logger=logger,
    )
