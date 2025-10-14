from sqlalchemy.exc import InvalidRequestError


def readonly(mapper, connection, target):
    raise InvalidRequestError(
        f"{mapper.class_.__name__} is Readonly (view), no changes allowed !"
    )