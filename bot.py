import discord
from discord.ext import commands
import os
import json
from utils.emojimgr import EmojiMgr
from utils.rchatmgr import RandchatMgr
from utils import checks

from data import configs, masters

secdir = configs.SECURE_DIR_PATH
tokenfile = configs.TOKEN_FILE_NAME if not configs.BETAMODE else configs.BETA_TOKEN_FILE_NAME

with open(os.path.join(secdir, tokenfile), 'r', encoding='utf-8') as file:
    token = file.read()

with open('./data/emojis.json', 'r', encoding='utf-8') as emojifile:
    emojis = json.load(emojifile)


bot = commands.Bot(command_prefix=';', status=discord.Status.dnd, activity=discord.Game('iNdirect 시작'))
bot.remove_command('help')

bot.add_check(checks.not_bot)

rmgr = RandchatMgr()
rmgr.start_match_task()

emj = EmojiMgr(bot, emojis['emoji-server'], emojis['emojis'])

bot.datas = {
    'emj': emj,
    'rmgr': rmgr
}

for ext in filter(lambda x: x.endswith('.py') and not x.startswith('_'), os.listdir('./exts')):
    bot.load_extension('exts.' + os.path.splitext(ext)[0])

bot.run(token)