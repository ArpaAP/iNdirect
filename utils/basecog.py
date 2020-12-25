import discord
from discord.ext import commands
from .rchatmgr import RandchatMgr
from .emojimgr import EmojiMgr

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.emj: EmojiMgr = bot.datas.get('emj')
        self.rmgr: RandchatMgr = bot.datas.get('rmgr')