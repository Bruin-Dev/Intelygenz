from collections import namedtuple

EdgeIdentifier = namedtuple(typename='EdgeIdentifier',
                            field_names=['host', 'enterprise_id', 'edge_id']
                            )


class EdgeIdentifier(EdgeIdentifier):
    __slots__ = ()

    def __str__(self):
        result = ", ".join(f"{field_name} = {value}" for field_name, value in self._asdict().items())
        return result
