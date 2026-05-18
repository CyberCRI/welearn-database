class InvalidURLScheme(Exception):
    """
    Scheme detected in URL is not accepted
    """

    def __init__(self, msg="URL schema is not accepted", *args):
        super().__init__(msg, *args)


class InvalidDOI(Exception):
    """
    Scheme detected in DOI is not accepted
    """

    def __init__(self, msg="DOI schema is not accepted", *args):
        super().__init__(msg, *args)


class ContentIsTooShort(Exception):
    """
    The string used as content is too short, it should be at least 25 characters long
    """

    def __init__(
        self,
        msg="Content is too short, it should be at least 25 characters long",
        *args,
    ):
        super().__init__(msg, *args)
