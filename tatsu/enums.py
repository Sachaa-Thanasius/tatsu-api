"""
tatsu.enums
-----------

Enumerations for the Tatsu API.
"""

from enum import Enum

__all__ = ("ActionType", "SubscriptionType")


class ActionType(Enum):
    """The way to modify a Tatsu user's score."""

    ADD = 0
    REMOVE = 1


class SubscriptionType(Enum):
    """The type of Tatsu subscription a user has."""

    NONE = 0
    SUPPORTER = 1
    SUPPORTER2 = 2
    SUPPORTER3 = 3

    def __str__(self) -> str:
        if self is SubscriptionType.NONE:
            return "None"
        return self.name.capitalize().replace(self.name[-1], "+" * int(self.name[-1]))
