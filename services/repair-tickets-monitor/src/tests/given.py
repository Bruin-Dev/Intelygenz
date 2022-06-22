from typing import Any
from unittest.mock import Mock


class Given(Mock):
    """
    Mock wrapper that builds a default side_effect that returns a given value
    when the calling arguments match the stored args and kwargs

    Given is a subclass of Mock, so any kwargs passed to the constructor will be set as instance members.
    For a Given instance to work the constructor must be passed both an `args` and a `kwargs` keyword arguments.
    """

    def returns(self, return_value: Any) -> "Given":
        def side_effect(*args, **kwargs):
            if self.args == args and self.kwargs == kwargs:
                return return_value

        self.side_effect = side_effect
        self.return_value = return_value
        return self


def given(*args, **kwargs) -> Given:
    """
    :param args: given args
    :param kwargs: given kwargs
    :return: a Given instance with the args and kwargs that need to be matched later.
    """

    # Given is a subclass of Mock, so any kwargs passed will be set as instance members.
    return Given(args=args, kwargs=kwargs)


def case(*givens: Given) -> Mock:
    """
    :param givens: tuple of givens
    :return: a single Mock which side effect will return the return_value of the first given
    that matches its args and kwargs with the mock call.
    """

    def side_effect(*args, **kwargs):
        for _given in givens:
            if _given.args == args and _given.kwargs == kwargs:
                return _given.return_value

    return Mock(side_effect=side_effect)
