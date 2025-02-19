class DuplicateError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class TokenRequestNotFoundError(Exception):
    pass


class RequestOnCooldownError(Exception):
    pass


class TooManyRequestError(Exception):
    pass


class WrongCredential(Exception):
    pass

