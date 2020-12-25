import discord
from discord.ext import commands
from utils.basecog import BaseCog

class Tasks(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
    
def setup(bot):
    cog = Tasks(bot)
    bot.add_cog(cog)