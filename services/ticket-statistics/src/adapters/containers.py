"""Adapters containers module."""
from dependency_injector import containers, providers

from .repositories.tickets.repo import TicketsRepository
from .config.settings import get_config
from .db.mongodb import IDB, MongoDB
from .db.redis import Redis
from .logger.logger import get_logger


class Adapters(containers.DeclarativeContainer):
    config = providers.Singleton(get_config)
    logger = providers.Singleton(get_logger, config=config)
    database: IDB = providers.Singleton(MongoDB, config=config, logger=logger)
    redis: Redis = providers.Singleton(Redis, config=config, logger=logger)

    # Repositories
    tickets_repository: TicketsRepository = providers.Singleton(
        TicketsRepository,
        database=database,
        logger=logger,
    )
