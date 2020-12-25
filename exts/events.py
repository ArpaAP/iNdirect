import discord
from discord.ext import commands
import asyncio
from utils.basecog import BaseCog
from data import colors
import traceback

class Events(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        bot.event(self.on_message)

    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인: {0}({0.id})'.format(self.bot.user))
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(';도움 입력'))

    async def on_message(self, message: discord.Message):
        if self.rmgr.is_matched(message.author.id):
            match: list = self.rmgr.get_matched(message.author.id)
            match.remove(message.author.id)

            if message.content == f'{self.bot.command_prefix}나가기':
                self.rmgr.exit_match(message.author.id)
                await message.author.send(
                    embed=discord.Embed(
                        title="↩ 랜덤 채팅을 종료했습니다!",
                        color=colors.SUCCESS
                    )
                )

                for one in map(self.bot.get_user, match):
                    asyncio.create_task(
                        one.send(
                            embed=discord.Embed(
                                description=f"**`{message.author}` 님이 채팅을 종료했습니다!**",
                                color=colors.PRIMARY
                            )
                        )
                    )

                return

            for one in map(self.bot.get_user, match):
                asyncio.create_task(one.send(message.content))
        
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