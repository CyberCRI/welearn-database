class WeLearnDatabaseException(Exception):
    """
    Base class for all WeLearnDatabase exceptions
    """


class InvalidURLScheme(WeLearnDatabaseException):
    """
    Scheme detected in URL is not accepted
    """

    def __init__(self, msg="URL schema is not accepted", *args):
        super().__init__(msg, *args)


class InvalidDOI(WeLearnDatabaseException):
    """
    Scheme detected in DOI is not accepted
    """

    def __init__(self, msg="DOI schema is not accepted", *args):
        super().__init__(msg, *args)


class ContentIsTooShort(WeLearnDatabaseException):
    """
    The string used as content is too short, it should be at least 25 characters long
    """

    def __init__(
        self,
        msg="Content is too short, it should be at least 25 characters long",
        *args,
    ):
        super().__init__(msg, *args)


class EarlyEnumerationVerificationError(WeLearnDatabaseException):
    """
    SQLAlchemy detect an enumeration value that is not in the list of accepted values
    """

    def __init__(
        self, msg="Enumeration value is not in the list of accepted values", *args
    ):
        super().__init__(msg, *args)
