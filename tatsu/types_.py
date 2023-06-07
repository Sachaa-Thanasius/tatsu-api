"""
tatsu.types_
------------

Typings/data structures for the Tatsu API.
"""

import datetime

from msgspec import Struct

__all__ = (
    "GuildMemberPoints",
    "GuildMemberScore",
    "GuildMemberRanking",
    "Ranking",
    "GuildRankings",
    "User",
)


class GuildMemberPoints(Struct):
    """A Discord guild member's points information.

    Parameters
    ----------
    guild_id : :class:`str`
        The Discord ID of the guild.
    points : :class:`int`
        The user's points.
    rank : :class:`int`
        The user's rank based on their points.
    user_id : :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    points: int
    rank: int
    user_id: str


class GuildMemberScore(Struct):
    """A Discord guild member's score information.

    Parameters
    ----------
    guild_id : :class:`str`
        The Discord ID of the guild.
    score : :class:`int`
        The user's score.
    user_id : :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    score: int
    user_id: str


class GuildMemberRanking(Struct, frozen=True):
    """A Discord guild member's ranking information over some period of time.

    Attributes
    ----------
    guild_id : :class:`str`
        The Discord ID of the guild.
    rank : :class:`int`
        The user's rank.
    score : :class:`int`
        The user's score.
    user_id : :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    rank: int
    score: int
    user_id: str


class Ranking(Struct, frozen=True):
    """A generic rank information object.

    Attributes
    ----------
    rank : :class:`int`
        The user's rank.
    score : :class:`int`
        The user's score.
    user_id : :class:`str`
        The user's Discord ID.
    """

    rank: int
    score: int
    user_id: str


class GuildRankings(Struct, frozen=True):
    """All the rankings in a guild over some period of time.

    Attributes
    ----------
    guild_id : :class:`str`
        The Discord ID of the guild.
    rankings : list[:class:`Ranking`]
        The rankings.
    """

    guild_id: str
    rankings: list[Ranking] = []


class User(Struct, frozen=True):
    """A Tatsu-bot user.

    Attributes
    ----------
    avatar_hash : class:`str`
        The user's Discord avatar hash.
    avatar_url : class:`str`
        The user's Discord avatar URL.
    credits : :class:`int`
        The amount of credits the user has.
    discriminator : class:`str`
        The user's 4 digit discriminator.
    id : class:`str`
        The user's Discord ID.
    info_box : class:`str`
        The text in the user's info box.
    reputation : :class:`int`
        The number of reputation points the user has.
    subscription_type : :class:`int`
        The user's subscription type.
    subscription_renewal : :class:`str`, optional
        The subscription renewal time if the user has a subscription.
    title : class:`str`
        The text in the user's title.
    tokens : :class:`int`
        The amount of tokens the user has.
    username : class:`str`
        The user's Discord username.
    xp : :class:`int`
        The number of experience points the user has.
    """

    avatar_hash: str
    avatar_url: str
    credits: int
    discriminator: str
    id: str
    info_box: str
    reputation: int
    subscription_type: int
    title: str
    tokens: int
    username: str
    xp: int
    subscription_renewal: datetime.datetime | None = None
