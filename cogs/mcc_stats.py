import requests
import discord
import json
import datetime
import aiohttp
import asyncio

from pony.orm import *
from os.path import exists
from discord.ext import commands

BASE_ENDPOINT          = "https://halo.api.stdlib.com/mcc@0.1.0/"
STATS_ENDPOINT         = "stats/"
GAMES_LATEST_ENDPOINT  = "games/latest/"
GAMES_HISTORY_ENDPOINT = "games/history/" 

CORRECT_GAMES = ["h1, h2, h2a, h3, h4, hr"]
CORRECT_GAME_VARIANT = [
    "Slayer",  
    "CTF", 
    "Oddball", 
    "KOTH", 
    "Juggernaut", 
    "Infection", 
    "Flood", 
    "Race", 
    "Extraction", 
    "Dominion", 
    "Regicide", 
    "Grifball", 
    "Ricochet", 
    "Forge", 
    "VIP"
]

db = Database()

class Gamer(db.Entity):
    discord_id = Required(str)
    gamertag   = Required(str)

if exists('xboxusers.sqlite') is False:
    db.bind(provider='sqlite', filename='xboxusers.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


class MCCStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def setxbox(self, ctx, *, gamertag: str):
        """ Set your gamertag """

        # This does the client connection to the MCC API. 
        # Normally, we'd do OAuth2 auth, but that's too 
        # complicated for this adventure.

        params = {"gamertag": gamertag}
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_ENDPOINT + STATS_ENDPOINT, params=params) as resp:
                returned_value = await resp.json()
            await session.close()

        # This is the first time I have worked with an ORM and a database.
        # This will check if the gamertag is correct first.
        # If it passes, it checks if the gamertag is already in the database.
        # If that passes, we add and commit.

        with db_session:
            if "error" in returned_value:
                await ctx.send("I'm sorry, but this gamertag is invalid. Try again with another one.")
            elif len(select(g for g in Gamer if g.discord_id == str(ctx.author.id))[:]) != 0:
                await ctx.send("You've already added your gamertag.")
            else:
                Gamer(discord_id=str(ctx.author.id), gamertag=gamertag)
                await ctx.send(f"I've set your gamertag to `{gamertag}`!")
        

    @commands.command()
    async def stats(self, ctx, *, gamertag = None):
        """ Grab stats about a Spartan """

        # When working with the database, we have to have this context manager.
        with db_session:
            if len(select(g for g in Gamer if g.discord_id == str(ctx.author.id))[:]) == 0:
                await ctx.send("You haven't linked your Gamertag. Use `/setxbox <gamertag>`.")
            else:
                params = {"gamertag": gamertag}
                async with aiohttp.ClientSession() as session:
                    async with session.get(BASE_ENDPOINT + STATS_ENDPOINT, params=params) as resp:
                        response = await resp.json()
                    await session.close()
                    
                embed = discord.Embed(
                    title=f"Stats for Spartan {gamertag}", 
                    colour=discord.Colour(0x40cf0f), 
                    timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp())
                )

                embed.set_thumbnail(url=response["emblem"])
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")

                embed.add_field(name="Clantag", value=response["clantag"], inline=True)
                embed.add_field(name="Playtime", value=response["playtime"], inline=True)
                embed.add_field(name="Games Played", value=response["gamesPlayed"], inline=True)
                embed.add_field(name="Wins", value=response["wins"], inline=True)
                embed.add_field(name="Losses", value=response["losses"], inline=True)
                embed.add_field(name="Win Ratio", value=response["winRatio"], inline=True)
                embed.add_field(name="Kills", value=response["kills"], inline=True)
                embed.add_field(name="Deaths", value=response["deaths"], inline=True)
                embed.add_field(name="Kill/Death Ratio", value=response["killDeathRatio"], inline=True)
                embed.add_field(name="Kills Per Game", value=response["killsPerGame"], inline=True)
                embed.add_field(name="Deaths Per Game", value=response["deathsPerGame"], inline=True)
                embed.add_field(name="Current Streak", value=response["streak"], inline=True)
                await ctx.send(embed=embed)


    # @commands.command()
    # async def latestgame(self, ctx, *, gamertag = None, game="All"):
    #     """ Grab latest game stats from a spartan's service record """
    #     FORMED_URL = BASE_ENDPOINT + GAMES_LATEST_ENDPOINT
    #     SHOULD_CONTINUE = True

    #     if game != "All" and game not in CORRECT_GAMES:
    #         await ctx.send("You'll need to use the correct game. Ex: h1, h2, h3, hr...")
    #         SHOULD_CONTINUE = False
        
    #     if gamertag is None:
    #         with open("user_to_xbox.json", "r") as f:
    #             gamertags = json.load(f)

    #         try:
    #             gamertag = gamertags[f"{ctx.author.id}"]
    #         except KeyError:
    #             await ctx.send("Your Gamertag is not set! Do it with the `/setxbox <your_gamertag>` command or give me a gamertag to use!")
    #             SHOULD_CONTINUE = False
    #     else:
    #         gamertag = gamertag

    #     if SHOULD_CONTINUE:
    #         payload = {"gamertag": gamertag, "game": game}
    #         response = requests.post(FORMED_URL, payload)

    #         embed = discord.Embed(
    #             title="Latest Game Stats for Spartan {}".format(gamertag), 
    #             colour=discord.Colour(0x40cf0f), 
    #             timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp())
    #         )

    #         embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    #         embed.add_field(name="Game Variant", value=response["games"][0]["gameVariant"], inline=True)
    #         embed.add_field(name="Map ID", value=response["games"][0]["mapId"], inline=True)
    #         embed.add_field(name="Won?", value=response["games"][0]["won"], inline=True)
    #         embed.add_field(name="Score", value=response["games"][0]["score"], inline=True)
    #         embed.add_field(name="Assists", value=response["games"][0]["assists"], inline=True)
    #         embed.add_field(name="Kills", value=response["games"][0]["kills"], inline=True)
    #         embed.add_field(name="Deaths", value=response["games"][0]["deaths"], inline=True)
    #         embed.add_field(name="Kill/Death Ratio", value=response["games"][0]["killDeathRatio"], inline=True)
    #         embed.add_field(name="Headshot Rate", value=response["games"][0]["headshotRate"], inline=True)
    #         embed.add_field(name="Played at...", value=response["games"][0]["playedAtRecency"], inline=True)
    #         embed.add_field(name="Headshots", value=response["games"][0]["headshots"], inline=True)
    #         embed.add_field(name="Medals", value=response["games"][0]["medals"], inline=True)        
    #         await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MCCStats(bot))