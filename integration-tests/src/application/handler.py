from typing import Any, Callable, Dict
from unittest.mock import AsyncMock

from pydantic import BaseModel
from starlette.responses import JSONResponse


class Handler(AsyncMock):
    """
    CouroutineMock wrapper that handles noop mocks
    """

    def noop(self) -> bool:
        return not self.return_value and not self.side_effect


class WillReturn(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self, return_value: Any):
        super().__init__(return_value=return_value)


class WillReturnJSON(WillReturn):
    """
    Handler expressive shorthand
    """

    def __init__(self, return_value: BaseModel | Dict[str, Any]):
        if isinstance(return_value, BaseModel):
            super().__init__(return_value=JSONResponse(return_value.dict()))
        else:
            super().__init__(return_value=JSONResponse(return_value))


class WillExecute(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self, execution: Callable[..., Any]):
        super().__init__(side_effect=execution)


class DoNothing(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self):
        super().__init__(return_value=None)
