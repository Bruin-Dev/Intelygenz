import asyncio

from src.application.actions.service_affecting_monitor import ServiceAffectingMonitor
from src.application.repositories.email_repository import EmailRepository
from src.application.repositories.notes_repository import NotesRepository
from src.application.repositories.trouble_repository import TroubleRepository
from src.application.repositories.utils_repository import UtilsRepository
from src.application.repositories.velocloud_repository import VelocloudRepository
from src.config import config
from src.logger.logger import LoggerClient


def handler(event, context):
    # LOGGER
    logger = LoggerClient(config).get_logger()
    logger.info(f"Service Affecting Monitor starting in {config.CURRENT_ENVIRONMENT}...")

    # REPOSITORIES
    utils_repository = UtilsRepository()
    email_repository = EmailRepository(logger=logger, config=config)
    velocloud_repository = VelocloudRepository(logger=logger, config=config, utils_repository=utils_repository)
    trouble_repository = TroubleRepository(config=config, utils_repository=utils_repository)
    notes_repository = NotesRepository(
        config=config, trouble_repository=trouble_repository, utils_repository=utils_repository
    )

    # ACTIONS
    service_affecting_monitor = ServiceAffectingMonitor(
        logger=logger,
        config=config,
        velocloud_repository=velocloud_repository,
        notes_repository=notes_repository,
        trouble_repository=trouble_repository,
        utils_repository=utils_repository,
        email_repository=email_repository,
    )

    asyncio.get_event_loop().run_until_complete(service_affecting_monitor.start_service_affecting_monitor())
