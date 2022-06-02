import re
from typing import Callable

import humps


class UtilsRepository:
    def convert_dict_to_snake_case(self, data: dict) -> dict:
        return self.convert_dict(data, self.to_snake_case)

    def convert_dict(self, d: dict, convert: Callable) -> dict:
        new_d = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_d[convert(k)] = self.convert_dict(v, convert)
            elif isinstance(v, list):
                new_d[convert(k)] = self.convert_list(v, convert)

            else:
                new_d[convert(k)] = v

        return new_d

    def convert_list(self, d: list, convert: Callable) -> list:
        new_d = []
        for v in d:
            if isinstance(v, dict):
                new_d.append(self.convert_dict(v, convert))
            elif isinstance(v, list):
                new_d.append(self.convert_list(v, convert))
            else:
                new_d.append(v)

        return new_d

    @staticmethod
    def to_snake_case(key: str) -> str:
        formatted_key = re.sub(r"[\W_]+", "", key)
        formatted_key = humps.decamelize(formatted_key)
        formatted_key = formatted_key.lower()

        return formatted_key
