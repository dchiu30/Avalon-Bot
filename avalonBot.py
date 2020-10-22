import discord
from discord.ext import commands

client = discord.Client()

tokenFile = open("token.txt", 'r')
token = tokenFile.read()
tokenFile.close()

bot = commands.Bot(command_prefix="ava.")
bot.load_extension("cogs.mainCog")
bot.run(token)
