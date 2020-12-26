import discord
from discord.ext import commands
import asyncio
from utils.basecog import BaseCog
from utils.rchatmgr import MatchItem
from data import colors
import traceback
from typing import List

class Events(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        bot.event(self.on_message)

    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인: {0}({0.id})'.format(self.bot.user))
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(';도움 입력'))

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) and self.rmgr.is_matched(message.author.id) and message.content[1:] not in ['나가기', '참여자']:
            match: List[MatchItem] = self.rmgr.get_matched(message.author.id)
            mymatch = next((m for m in match if m.uid == message.author.id), None)
            match.remove(mymatch)

            await asyncio.gather(
                *(one.send('**[{}]** {}'.format(mymatch.altnick or message.author, message.content)) for one in map(self.bot.get_user, map(lambda x: x.uid, match))),
                return_exceptions=True
            )
        
        else:
            await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.errors.PrivateMessageOnly):
            await ctx.send(
                embed=discord.Embed(
                    title='⛔ DM 전용 명령어',
                    description='이 명령어는 개인 메시지에서만 사용할 수 있습니다!',
                    color=colors.ERROR
                )
            )

        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=discord.Embed(
                    title='⛔ 개발자 전용 명령어',
                    description='이 명령어는 개발자만 사용할 수 있습니다.',
                    color=colors.ERROR
                )
            )

        elif isinstance(error, commands.CommandNotFound):
            pass

        else:
            tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            print(tb)
            await ctx.send(
                embed=discord.Embed(
                    title="❌ 오류가 발생했습니다!",
                    description=f'```python\n{tb}```',
                    color=colors.ERROR
                )
            )
        
def setup(bot):
    cog = Events(bot)
    bot.add_cog(cog)