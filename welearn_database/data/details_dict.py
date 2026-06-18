from dataclasses import asdict, is_dataclass

from sqlalchemy import types


class DetailsDict(types.TypeDecorator):
    """
    Convert dataclass instances into dictionaries for JSON storage.
    """

    impl = types.JSON
    cache_ok = True

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
        # Serialize recursively without mutating the original object stored on the ORM instance.
        return self._inner_serialize_dataclass(value)
