import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import time
import datetime
import requests
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
url = "192.168.129.41:8000/"
startup_time = datetime.datetime.now()
bot = commands.Bot(command_prefix="*", intents=intents)
@bot.event
async def on_ready():
    print(f"{time.ctime()} Offtool is nu online, BOT NAAM: {bot.user.name}")


@bot.command()
async def runtime(ctx):

    await ctx.send(datetime.datetime.now()- startup_time)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "sigma":
        await message.delete()
        await message.channel.send("Heel sigma van jou maar niet nu")
    await bot.process_commands(message)
bot.run(token, log_handler=handler, log_level=logging.DEBUG)