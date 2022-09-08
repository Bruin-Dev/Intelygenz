from typing import Any, Callable, Dict, Optional
from unittest.mock import AsyncMock

from pydantic import BaseModel
from starlette.responses import JSONResponse


class Handler(AsyncMock):
    """
    CouroutineMock wrapper that handles noop mocks
    """

    def returns_nothing(self) -> bool:
        return not self.return_value and not self.side_effect


class WillReturn(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self, return_value: Any, headers: Optional[Dict] = None):
        super().__init__(return_value=return_value, headers=headers)


class WillReturnJSON(WillReturn):
    """
    Handler expressive shorthand
    """

    def __init__(self, return_value: BaseModel | Any, headers: Optional[Dict] = None):
        if isinstance(return_value, BaseModel):
            super().__init__(return_value=JSONResponse(return_value.dict(), headers=headers))
        else:
            super().__init__(return_value=JSONResponse(return_value, headers=headers))


class WillExecute(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self, execution: Callable[..., Any]):
        super().__init__(side_effect=execution)


class WillReturnNothing(Handler):
    """
    Handler expressive shorthand
    """

    def __init__(self):
        super().__init__(return_value=None)
