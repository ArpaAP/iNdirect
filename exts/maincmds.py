import discord
from discord.ext import commands
import asyncio
from data import colors
from utils.basecog import BaseCog
from utils import rchatmgr
from datetime import timedelta
import time
import math
from typing import Optional
from itertools import cycle
import random
from db import randnick, helps

class MainCmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.dm_only()
    @commands.command(name='랜덤채팅')
    async def _randchat(self, ctx: commands.Context, count: Optional[int]=2):
        if not 2 <= count:
            await ctx.send(
                embed=discord.Embed(
                    title="❗ 인원수는 최소 2명입니다!",
                    description="인원수는 자신도 포함한 수입니다!",
                    color=colors.ERROR
                )
            )

        msg = await ctx.send(
            embed=discord.Embed(
                title=f'💬 {count}인 개인 랜덤채팅 매칭을 시작할까요?',
                description=f'자신을 포함해 전체 {count}명을 매칭하게 됩니다.\n\n**채팅 모드를 선택하세요:**\n\n🏷: **일반 모드**\n> 이름과 태그가 표시됩니다.\n\n❔: **익명 모드**\n> 이름과 태그 대신 랜덤으로 생성한 닉네임을 사용합니다.',
                color=colors.PRIMARY
            ).set_footer(text="❌ 를 클릭해 취소합니다.")
        )

        checkemj = '✅'
        crossemj = '❌'
        emjs = '🏷', '❔', crossemj

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
            if reaction.emoji != crossemj:
                if self.rmgr.is_in_queue(ctx.author.id):
                    return

                if reaction.emoji == '❔':
                    altnick = ' '.join([random.choice(randnick.FIRST), random.choice(randnick.LAST)])
                else:
                    altnick = None

                rainbow = cycle(map(lambda x: x/35, range(0, 36)))

                def get_matching_embed(time_elapsed_seconds: float=None):
                    embed = discord.Embed(
                        title='{} 채팅 상대를 매칭 중입니다...'.format(self.emj.get(ctx, "loading")),
                        color=discord.Color.from_hsv(next(rainbow), 1, 0.9)
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
                    match = await self.rmgr.start_match(ctx.author.id, count=count-1, altnick=altnick, timeout=5*60)
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
                        members = "`" + "`님, `".join(o.altnick or str(self.bot.get_user(o.uid)) for o in match if o.uid != ctx.author.id) + "`"
                        await ctx.send(
                            embed=discord.Embed(
                                title=f'{checkemj} 매칭됐습니다!',
                                description=(f'당신의 별명은 `{altnick}` 입니다!\n' if altnick else '') + members + '와(과) 매칭되었습니다.',
                                color=colors.SUCCESS
                            ).set_footer(text=f'{self.bot.command_prefix}나가기 명령으로 랜덤채팅에서 나갈 수 있습니다.')
                        )

                finally:
                    cancel_task.cancel()
                    time_counter_task.cancel()

    @commands.dm_only()
    @commands.command(name="나가기")
    async def _exit(self, ctx: commands.Context):
        if self.rmgr.is_matched(ctx.author.id):
            match = self.rmgr.get_matched(ctx.author.id)
            self.rmgr.exit_match(ctx.author.id)
            await ctx.author.send(
                embed=discord.Embed(
                    title="↩ 랜덤 채팅을 나갔습니다!",
                    color=colors.SUCCESS
                )
            )

            await asyncio.gather(
                *(
                    one.send(
                        embed=discord.Embed(
                            description=f"**`{ctx.author}` 님이 채팅을 나갔습니다!**",
                            color=colors.WARN
                        )
                    )
                    for one in map(self.bot.get_user, map(lambda x: x.uid, match)) if one.id != ctx.author.id
                ),
                return_exceptions=True
            )

            if len(match) == 2:
                await self.bot.get_user(list(filter(lambda x: x.uid != ctx.author.id, match))[0].uid).send(
                    embed=discord.Embed(
                        description="대화 상대가 모두 나가 랜덤채팅이 종료되었습니다.",
                        color=colors.PRIMARY
                    )
                )
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="❌ 이 명령어는 랜덤채팅 중에만 사용할 수 있습니다!",
                    description="이미 채팅을 나간것으로 보입니다!",
                    color=colors.ERROR
                )
            )

    @commands.dm_only()
    @commands.command(name="참여자")
    async def _people(self, ctx: commands.Context):
        if self.rmgr.is_matched(ctx.author.id):
            match = self.rmgr.get_matched(ctx.author.id)
            
            await ctx.send(
                embed=discord.Embed(
                    title="📋 채팅 참여자 목록",
                    description="\n".join(map(lambda x: (x.altnick or str(self.bot.get_user(x.uid))) + (' (나)' if x.uid == ctx.author.id else ''), match)),
                    color=colors.PRIMARY
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="❌ 이 명령어는 랜덤채팅 중에만 사용할 수 있습니다!",
                    color=colors.ERROR
                )
            )

    @commands.command(name="도움", aliases=['명령', '명령어', 'help'])
    async def _help(self, ctx: commands.Context):
        embed = discord.Embed(
            title="iNdirect 전체 명령어",
            description=helps.COMMANDS.format(p=self.bot.command_prefix),
            color=colors.PRIMARY
        )
        if ctx.channel.type != discord.ChannelType.private:
            msg, sending = await asyncio.gather(
                ctx.author.send(embed=embed),
                ctx.send(
                    embed=discord.Embed(
                        title="{} 도움말을 전송하고 있습니다...".format(self.emj.get(ctx, "loading")),
                        color=colors.PRIMARY,
                    )
                )
            )
            await sending.edit(
                embed=discord.Embed(
                    title="{} 도움말을 전송했습니다!".format(self.emj.get(ctx, "check")),
                    description=f"**[DM 메시지]({msg.jump_url})**를 확인하세요!",
                    color=colors.SUCCESS,
                )
            )
        else:
            msg = await ctx.author.send(embed=embed)

def setup(bot):
    cog = MainCmds(bot)
    bot.add_cog(cog)
