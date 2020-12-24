import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인: {0}({0.id})'.format(bot.user))
        await client.change_presence(status=discord.Status.online)
        
def setup(bot):
    cog = Events(bot)
    bot.add_cog(cog)