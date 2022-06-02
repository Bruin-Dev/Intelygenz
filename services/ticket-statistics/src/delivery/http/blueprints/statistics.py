import threading

from adapters.containers import Adapters
from adapters.db.redis import Redis
from dateutil.parser import isoparse
from dependency_injector.wiring import Provide, inject
from usecases.containers import UseCases
from usecases.statistics import StatisticsUseCase


@inject
def get_blueprint(
    logger=Provide[Adapters.logger],
    redis: Redis = Provide[Adapters.redis],
    statistics_use_case: StatisticsUseCase = Provide[UseCases.statistics_use_case],
):
    from delivery.http.handlers import response_handler
    from delivery.http.handlers.exceptions.project_exception import ProjectException
    from delivery.http.handlers.tags.response import RESPONSES
    from flask import Response, request
    from flask_smorest import Blueprint

    endpoint = "/statistics"
    name = "statistics"

    blueprint = Blueprint(name, __name__, template_folder="blueprints")
    lock = threading.Lock()

    @blueprint.route(endpoint, methods=["GET"], strict_slashes=False)
    def get_statistics() -> Response:
        """Get statistics data between dates"""
        start = request.args.get("start")
        end = request.args.get("end")

        if not start or not end:
            raise ProjectException("MISSING_DATES")

        try:
            start_date = isoparse(start)
            end_date = isoparse(end)
        except ValueError:
            raise ProjectException("INVALID_DATES")

        if start_date > end_date:
            raise ProjectException("INVALID_DATE_RANGE")

        with lock:
            statistics = redis.get(start, end)
            cache_hit = bool(statistics)

            if statistics:
                logger.info(f"Found statistics between {start} and {end} on Redis, skipping calculation")
            else:
                statistics = statistics_use_case.calculate_statistics(start=start_date, end=end_date)
                redis.set(statistics, start, end)

        metadata = {"cache_hit": cache_hit}
        return response_handler.response(tag=RESPONSES["RESOURCE_FOUND"], data=statistics, metadata=metadata)

    return blueprint
