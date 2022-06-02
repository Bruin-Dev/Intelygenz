import traceback

from delivery.http.handlers.exceptions.project_exception import ProjectException
from flask import jsonify


def get_error_with_exception(exception):
    if hasattr(exception, "serialize"):
        return exception.serialize
    else:
        return exception


def constructor_error_handler(logger):
    def send_error(exception):
        logger.exception(exception)
        error = get_error_with_exception(exception)

        if isinstance(exception, ProjectException):
            return jsonify(error), int(error["code"])

        trace = traceback.format_exc()
        exception = ProjectException(tag="INTERNAL_ERROR", trace=trace)
        error = get_error_with_exception(exception)

        return jsonify(error), int(error["code"])

    return send_error
