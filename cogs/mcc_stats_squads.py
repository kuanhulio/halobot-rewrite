import discord
import datetime
import aiohttp

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

class Squads(Gamer):
    squad_name  = Required(str)
    coowner     = Optional(str)
    members     = Optional(StrArray)
    channel_ids = Required(StrArray)
    role_ids    = Required(StrArray)


db.bind(provider='sqlite', filename='xboxusers.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

class MCCStatsAndSquads(commands.Cog):
    """Get your Spartan Stats from the Halo: The Master Chief Collection"""
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

def setup(bot):
    bot.add_cog(MCCStatsAndSquads(bot))