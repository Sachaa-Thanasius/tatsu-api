"""
tatsu.enums
-----------

Enumerations for the Tatsu API.
"""

from enum import Enum

__all__ = ("ActionType", "SubscriptionType", "CurrencyType")


class ActionType(Enum):
    """The way to modify a Tatsu user's score."""

    ADD = 0
    REMOVE = 1


class SubscriptionType(Enum):
    """The type of Tatsu subscription a user has."""

    NONE = 0
    SUPPORTER1 = 1
    SUPPORTER2 = 2
    SUPPORTER3 = 3


class CurrencyType(Enum):
    """A type of Tatsu currency."""

    CREDITS = 0
    TOKENS = 1
    EMERALDS = 2
    CANDY_CANE = 3
    USD = 4
    CANDY_CORN = 5
