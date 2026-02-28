"""
Custom exceptions for the message publishing system.

This module defines custom exception classes for the message publishing system.
These exceptions provide more specific error handling for different failure
scenarios that can occur during message publication.
"""


class PublisherError(Exception):
    """Base exception for publisher errors."""

    pass


class PublishTimeoutError(PublisherError):
    """Raised when a message publishing times out."""


class PublishFailedError(PublisherError):
    """Raised when a message fails to
    publish for reasons other than timeout."""
