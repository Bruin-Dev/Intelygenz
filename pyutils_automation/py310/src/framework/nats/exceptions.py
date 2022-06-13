from nats import errors


class NatsException(Exception):
    """
    Exception class from which every exception in this library will derive.
    It enables consumers of this library to catch all errors coming from the library using a single except statement.
    """

    pass


class NatsConnectionError(NatsException):
    """
    Represents a connection error with NATS.
    """

    pass


class SubjectBoundException(NatsException):
    """
    Represents an error related to a particular NATS subject.
    """

    def __init__(self, subject: str):
        super().__init__()
        self.__subject = subject

    def __str__(self) -> str:
        return f'[subject="{self.__subject}"] {super().__str__()}'


class BadSubjectError(SubjectBoundException, errors.BadSubjectError):
    """
    Represents an error related to a subject not allowed by NATS.
    """

    pass


class ResponseTimeoutError(SubjectBoundException, errors.TimeoutError):
    """
    Represents a timeout error while awaiting a response in a NATS Request-Reply flow.
    """

    pass
