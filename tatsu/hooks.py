import msgspec

from .models import (
    GuildMemberPoints,
    GuildMemberRanking,
    GuildMemberScore,
    GuildRankings,
    StoreListing,
    User,
)


# fmt: off
GEN_ENCODER                     = msgspec.json.Encoder()
GEN_DECODER                     = msgspec.json.Decoder()
GUILD_MEMBER_POINTS_DECODER     = msgspec.json.Decoder(GuildMemberPoints)
GUILD_MEMBER_SCORE_DECODER      = msgspec.json.Decoder(GuildMemberScore)
GUILD_MEMBER_RANKING_DECODER    = msgspec.json.Decoder(GuildMemberRanking)
GUILD_RANKINGS_DECODER          = msgspec.json.Decoder(GuildRankings)
USER_DECODER                    = msgspec.json.Decoder(User)
STORE_LISTING_DECODER           = msgspec.json.Decoder(StoreListing)
# fmt: on
