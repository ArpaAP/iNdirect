import discord
from discord.ext import commands

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
def setup(bot):
    cog = Tasks(bot)
    bot.add_cog(cog)