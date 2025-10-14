from sqlalchemy import event

from welearn_database.modules.views_helper import readonly


class ReadOnlyViewMixin:
    """
    Mixin to make a SQLAlchemy model read-only by listening to events that would modify data.
    """
    __readonly__ = True

    # https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#declare-last
    @classmethod
    def __declare_last__(cls):
        """ Listen for the SQLAlchemy events and raise on any attempt to change data """
        for sqla_event in ("before_insert", "before_update", "before_delete", "before_flush"):
            event.listen(cls, sqla_event, readonly, propagate=True)