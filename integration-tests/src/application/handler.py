import logging
from typing import Any, Callable

from asynctest import CoroutineMock

log = logging.getLogger(__name__)


class Handler(CoroutineMock):
    def noop(self) -> bool:
        return not self.return_value and not self.side_effect


class WillReturn(Handler):
    def __init__(self, return_value: Any):
        super().__init__(return_value=return_value)


class WillExecute(Handler):
    def __init__(self, execution: Callable[..., Any]):
        super().__init__(side_effect=execution)


class DoNothing(Handler):
    def __init__(self):
        super().__init__(return_value=None)
