from dataclasses import asdict, is_dataclass

from sqlalchemy import types


class DetailsDict(types.TypeDecorator):
    """
    Convert all dataclass into dict
    """

    impl = types.JSON

    @staticmethod
    def _is_dataclass_instance(obj):
        return is_dataclass(obj) and not isinstance(obj, type)

    def _inner_serialize_dataclass(self, value):
        match value:
            case list():
                return [self._inner_serialize_dataclass(item) for item in value]
            case dict():
                return {k: self._inner_serialize_dataclass(v) for k, v in value.items()}
        if self._is_dataclass_instance(value):
            return asdict(value)
        return value

    def process_bind_param(self, value, dialect):
        if isinstance(value, dict):
            for detail_key, detail_value in value.items():
                match detail_value:
                    case list():
                        value[detail_key] = [
                            self._inner_serialize_dataclass(item)
                            for item in detail_value
                        ]
                    case dict():
                        for k, v in detail_value.items():
                            detail_value[k] = self._inner_serialize_dataclass(v)
                        value[detail_key] = detail_value
                    case _:
                        value[detail_key] = self._inner_serialize_dataclass(
                            detail_value
                        )
        return value
