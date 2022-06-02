from typing import Dict

from delivery.http.handlers.tags.error import ERRORS


class ProjectException(Exception):
    def __init__(self, tag=None, trace=None, message=None, show_trace=False, dynamic_error: Dict = None):
        self.tag = tag
        self.trace = trace
        self.message = message
        self.show_trace = show_trace

        if self.tag in ERRORS:
            self.__set_properties(ERRORS[tag], message)
        elif dynamic_error:
            self.__set_properties(dynamic_error, None)
        else:
            self.__set_properties(ERRORS["INTERNAL_ERROR"], message)

    def __set_properties(self, error, message):
        self.message = error["message"]
        self.code = error["code"]

        if message is not None:
            self.message = message

    @property
    def serialize(self):
        return {"code": self.code, "tag": self.tag, "message": self.message}
