import discord
from discord.ext import commands
import asyncio
from utils.basecog import BaseCog
import traceback
from utils import checks
from data import colors

class Mastercmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @checks.is_master()
    @commands.command(name='eval')
    async def _eval(self, ctx: commands.Context, *, arg):
        try:
            rst = eval(arg)
        except:
            evalout = f'📥INPUT: ```python\n{arg}```\n💥EXCEPT: ```python\n{traceback.format_exc()}```\n{self.emj.get(ctx, "cross")} ERROR'
        else:
            evalout = f'📥INPUT: ```python\n{arg}```\n📤OUTPUT: ```python\n{rst}```\n{self.emj.get(ctx, "check")} SUCCESS'
        embed=discord.Embed(title='**💬 EVAL**', color=colors.PRIMARY, description=evalout)
        await ctx.send(embed=embed)

    @checks.is_master()
    @commands.command(name='exec')
    async def _exec(self, ctx: commands.Context, *, arg):
        try:
            exec(arg)
        except:
            evalout = f'📥INPUT: ```python\n{arg}```\n💥EXCEPT: ```python\n{traceback.format_exc()}```\n{self.emj.get(ctx, "cross")} ERROR'
        else:
            evalout = f'📥INPUT: ```python\n{arg}```\n{self.emj.get(ctx, "check")} SUCCESS'
        embed=discord.Embed(title='**💬 EXEC**', color=colors.PRIMARY, description=evalout)
        await ctx.send(embed=embed)

    @checks.is_master()
    @commands.command(name='await')
    async def _await(self, ctx: commands.Context, *, arg):
        try:
            rst = await eval(arg)
        except:
            evalout = f'📥INPUT: ```python\n{arg}```\n💥EXCEPT: ```python\n{traceback.format_exc()}```\n{self.emj.get(ctx, "cross")} ERROR'
        else:
            evalout = f'📥INPUT: ```python\n{arg}```\n📤OUTPUT: ```python\n{rst}```\n{self.emj.get(ctx, "check")} SUCCESS'
        embed=discord.Embed(title='**💬 AWAIT**', color=colors.PRIMARY, description=evalout)
        await ctx.send(embed=embed)

    @checks.is_master()
    @commands.command(name='hawait')
    async def _hawait(self, ctx: commands.Context, *, arg):
        try:
            await eval(arg)
        except:
            await ctx.send(embed=discord.Embed(title='❌ 오류', color=colors.ERROR))
    
def setup(bot):
    cog = Mastercmds(bot)
    bot.add_cog(cog)