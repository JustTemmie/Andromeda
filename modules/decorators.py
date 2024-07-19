from discord.ext import commands

import os
import time

import functools

def is_host_owner():
    async def predicate(ctx) -> bool:
        if ctx.author.id in ctx.bot.config["HOST_OWNERS"]:
            return True
        else:
            raise commands.NotOwner(ctx.bot.lang.tr("error_not_responsible_for_host", hostname=os.uname()[1]))
        
    return commands.check(predicate)


# a wrapper for funcstools.lru_cache() that only holds data for x seconds
def time_cache(maxAgeSeconds, maxSize=128):
    def _decorator(func):
        @functools.lru_cache(maxsize=maxSize)
        def _new(*args, __time_salt, **kwargs):
            return func(*args, **kwargs)

        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / maxAgeSeconds))

        return _wrapped

    return _decorator