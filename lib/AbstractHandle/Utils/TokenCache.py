
from cachetools import (
    Cache,
    TTLCache
)
from datetime import datetime


def epoch_ms():
    return int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)


class TokenCache(TTLCache):
    """
    Extends the TTLCache to handle KBase auth tokens.
    So they have a base expiration of 5 minutes,
    but expire sooner if the token itself expires.
    """

    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        token = super(TokenCache, self).__getitem__(key, cache_getitem=cache_getitem)
        if token.get('expires', 0) <= epoch_ms():
            return None
        else:
            return token
