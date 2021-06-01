import traceback

from flask import jsonify

from delivery.http.handlers.exceptions.project_exception import ProjectException


def get_error_with_exception(exception):
    return exception.serialize


def constructor_error_handler(logger):
    def send_error(exception):
        logger.exception(exception)
        error = get_error_with_exception(exception)

        if isinstance(exception, ProjectException):
            return jsonify(error), int(error['code'])

        trace = traceback.format_exc()
        exception = ProjectException(tag='INTERNAL_ERROR', trace=trace)
        error = get_error_with_exception(exception)

        return jsonify(error), int(error['code'])

    return send_error
