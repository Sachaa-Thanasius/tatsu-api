"""
tatsu.errors
------------

Exceptions for the Tatsu API.
"""

__all__ = (
    "TatsuException",
    "TatsuAPIException",
    "UnknownUser",
    "UnknownGuild",
    "UnknownGuildMember",
    "NotInGuild",
    "MissingPermission",
    "InsufficientScore",
    "InsufficientPoints",
)


class TatsuException(Exception):
    """Base exception class for Tatsu."""


class TatsuAPIException(TatsuException):
    """Exception that's raised when Tatsu's API sends back a specific error."""


class UnknownUser(TatsuException):
    """Exception that's raised when Tatsu can't find a user."""


class UnknownGuild(TatsuException):
    """Exception that's raised when Tatsu can't find a guild."""


class UnknownGuildMember(TatsuException):
    """Exception that's raised when Tatsu can't find a guild member."""


class NotInGuild(TatsuException):
    """Exception that's raised when the user isn't in a guild it's attempting to get information about."""


class MissingPermission(TatsuException):
    """Exception that's raised when the user needs the MANAGE_GUILD permission to do something."""


class InsufficientScore(TatsuException):
    """Exception that's raised when a member doesn't have a high enough score to remove some amount."""


class InsufficientPoints(TatsuException):
    """Exception that's raised when a member doesn't have enough points to remove some amount."""
