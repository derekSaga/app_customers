class PublisherError(Exception):
    """Base exception for publisher errors."""

    pass


class PublishTimeoutError(PublisherError):
    """Raised when a message publishing times out."""


class PublishFailedError(PublisherError):
    """Raised when a message fails to
    publish for reasons other than timeout."""
