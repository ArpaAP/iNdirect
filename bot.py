import discord
from discord.ext import commands
import os
import json
from utils.emojimgr import EmojiMgr

from data import configs

secdir = configs.SECURE_DIR_PATH
tokenfile = configs.TOKEN_FILE_NAME if not configs.BETAMODE else configs.BETA_TOKEN_FILE_NAME

with open(os.path.join(secdir, tokenfile), 'r', encoding='utf-8') as file:
    token = file.read()

with open('./data/emojis.json', 'r', encoding='utf-8') as emojifile:
    emojis = json.load(emojifile)

bot = commands.Bot(command_prefix=';', status=discord.Status.dnd, activity=discord.Game('iNdirect 시작 중'))
bot.remove_command('help')

emj = EmojiMgr(bot, emojis['emoji-server'], emojis['emojis'])

for ext in filter(lambda x: x.endswith('.py'), os.listdir('./exts')):
    bot.load_extension('exts.' + os.path.splitext(ext)[0])

bot.datas = {
    'emj': emj
}

bot.run(token)