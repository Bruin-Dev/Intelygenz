class UnexpectedStatusError(Exception):
    def __init__(self, status: int):
        self.status = status
        super().__init__(f"Unexpected response status: {status}")


class UnknownStatusError(Exception):
    def __init__(self, status: str):
        self.status = status
        super().__init__(f"Unknown device status: {status}")


class UnexpectedResponseError(Exception):
    pass
