class JarvisError(Exception):
    """Base exception for expected application failures."""


class ConfigurationError(JarvisError):
    pass


class ServiceUnavailableError(JarvisError):
    pass


class CommandNotFoundError(JarvisError):
    pass


class ConfirmationRequiredError(JarvisError):
    pass
