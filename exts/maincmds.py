import discord
from discord.ext import commands
import asyncio
from data import colors
from utils.basecog import BaseCog
from utils import rchatmgr
from datetime import timedelta
import time
import math

class MainCmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.dm_only()
    @commands.command(name='랜덤채팅')
    async def _randchat(self, ctx: commands.Context):
        msg = await ctx.send(
            embed=discord.Embed(
                title='💬 개인 랜덤채팅 매칭을 시작할까요?',
                description='랜덤채팅 상대에게 내 태그를 제외한 닉네임이 표시됩니다.',
                color=colors.PRIMARY
            )
        )

        checkemj = self.emj.get(ctx, 'check')
        crossemj = self.emj.get(ctx, 'cross')
        emjs = checkemj, crossemj

        for emj in emjs:
            await msg.add_reaction(emj)

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user == ctx.author and msg.id == reaction.message.id and reaction.emoji in emjs)
        except asyncio.TimeoutError:
            try:
                await msg.delete()
            except: pass
        else:
            await msg.delete()
            if reaction.emoji == checkemj:
                if self.rmgr.is_in_queue(ctx.author.id):
                    return

                def get_matching_embed(time_elapsed_seconds: float=None):
                    embed = discord.Embed(
                        title='{} 채팅 상대를 매칭 중입니다...'.format(self.emj.get(ctx, "loading")),
                        color=colors.PRIMARY
                    )

                    footermsg = '❌ 로 반응해 매칭을 취소할 수 있습니다.'

                    if time_elapsed_seconds:
                        embed.set_footer(text=f"{footermsg} {timedelta(seconds=time_elapsed_seconds)} 지남")
                    else:
                        embed.set_footer(text=footermsg)

                    return embed

                start = time.time()

                matchmsg = await ctx.send(
                    embed=get_matching_embed(0)
                )
                await matchmsg.add_reaction('❌')

                async def cancel_waitfor():
                    try:
                        await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and matchmsg.id == reaction.message.id and reaction.emoji == '❌')
                    finally:
                        self.rmgr.cancel_match(ctx.author.id)

                async def time_elapsed_counter():
                    while True:
                        await matchmsg.edit(
                            embed=get_matching_embed(math.trunc(time.time() - start))
                        )
                        await asyncio.sleep(1)

                cancel_task = asyncio.create_task(cancel_waitfor())
                time_counter_task = asyncio.create_task(time_elapsed_counter())
                    
                try:
                    match = await self.rmgr.start_match(ctx.author.id, count=2, timeout=5*60)
                except asyncio.TimeoutError:
                    cancel_task.cancel()
                    time_counter_task.cancel()
                    try:
                        await matchmsg.delete()
                    finally:
                        await ctx.send(
                            embed=discord.Embed(
                                title='⏰ 매칭 상대를 찾지 못했습니다. 시간이 초과되었습니다!',
                                color=colors.ERROR
                            )
                        )
                except rchatmgr.MatchCanceled:
                    cancel_task.cancel()
                    time_counter_task.cancel()
                    try:
                        await matchmsg.delete()
                    finally:
                        await ctx.send(
                            embed=discord.Embed(
                                title='❌ 매칭을 취소했습니다.',
                                color=colors.ERROR
                            )
                        )

                else:
                    cancel_task.cancel()
                    time_counter_task.cancel()
                    try:
                        await matchmsg.delete()
                    finally:
                        members = "`" + "`님, `".join(str(self.bot.get_user(o)) for o in match if o != ctx.author.id) + "`"
                        await ctx.send(
                            embed=discord.Embed(
                                title=f'{checkemj} 매칭됐습니다!',
                                description=members + '와(과) 매칭되었습니다.',
                                color=colors.SUCCESS
                            )
                        )

def setup(bot):
    cog = MainCmds(bot)
    bot.add_cog(cog)