from discord.ext import commands
from data import masters

async def master_only(ctx):
    if ctx.author.id in masters.MASTERS:
        return True
    raise commands.NotOwner()

def is_master():
    return commands.check(master_only)

async def not_bot(ctx):
    if not ctx.author.bot:
        return True
    raise commands.CheckFailure