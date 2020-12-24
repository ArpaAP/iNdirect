import discord
from discord.ext import commands

class EmojiMgr:
    def __init__(self, client: discord.Client, guild: int, emojis: dict):
        self.guild = guild
        self.emojis = emojis
        self.client = client

    def get(self, ctx: commands.Context, name: str):
        if not ctx.guild or ctx.channel.permissions_for(ctx.guild.get_member(self.client.user.id)).external_emojis:
            return self.client.get_emoji(self.emojis[name]['default'])
        else:
            try:
                rt = self.emojis[name]['replace']
            except KeyError:
                rt = ''
            return rt

    def getid(self, name):
        return self.emojis[name]