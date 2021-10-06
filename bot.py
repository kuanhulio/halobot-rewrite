import os
import discord
import json
from pretty_help import PrettyHelp
from discord.ext import commands

with open("config.json", "r") as f:
    config = json.load(f)

bot = commands.Bot(command_prefix=config["prefix"],
                   prefix=config["prefix"],
                   owner_ids=config["owners"],
                   command_attrs=dict(hidden=True),
                   help_command=PrettyHelp(),
                   intents=discord.Intents(guilds=True,
                                           members=True,
                                           messages=True,
                                           reactions=True,
                                           presences=True))

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(config["token"])
except Exception as e:
    print(f'Error when logging in: {e}')
