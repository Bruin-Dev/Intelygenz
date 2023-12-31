from collections import namedtuple

nats_error_response = {"body": None, "status": 503}

EdgeIdentifier = namedtuple(
    typename="EdgeIdentifier",
    field_names=["host", "enterprise_id", "enterprise_name", "edge_id"])


class EdgeIdentifier(EdgeIdentifier):
    __slots__ = ()

    def __str__(self):
        result = ", ".join(f"{field_name} = {value}" for field_name, value in self._asdict().items())
        return result
