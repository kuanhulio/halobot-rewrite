import discord
import datetime
import aiohttp

from pony.orm import *
from discord.ext import commands

BASE_ENDPOINT          = "https://halo.api.stdlib.com/mcc@0.1.0/"
STATS_ENDPOINT         = "stats/"
GAMES_LATEST_ENDPOINT  = "games/latest/"
GAMES_HISTORY_ENDPOINT = "games/history/" 

CORRECT_GAMES = ["h1", "h2", "h2a", "h3", "h4", "hr"]
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


# class Squads(Gamer):
#     squad_name  = Required(str)
#     coowner     = Optional(str)
#     members     = Optional(StrArray)
#     channel_ids = Required(StrArray)
#     role_ids    = Required(StrArray)

db.bind(provider='sqlite', filename='xboxusers.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

async def gamertag_getter(gamertag: str, game: str = None, game_variant: str = None, checker: int =1):
    # This function obfuscates the API calls so my regular functions look nice.
    # Checker = 1 means it's a Stats call
    # Checker = 2 means it's a Latest Game Call
    # TODO: Add more checks if needed.
    if checker == 1: 
        params = {"gamertag": gamertag}
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_ENDPOINT + STATS_ENDPOINT, params=params) as resp:
                returned_value = await resp.json()
            await session.close()
            return returned_value
    elif checker == 2:
        params = {"gamertag": gamertag, "game": game, "gameVariant": game_variant}
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_ENDPOINT + GAMES_LATEST_ENDPOINT, params=params) as resp:
                returned_value = await resp.json()
            await session.close()
            return returned_value 

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

        response = await gamertag_getter(gamertag=gamertag, game=None, game_variant=None, checker=1)

        # This is the first time I have worked with an ORM and a database.
        # This will check if the gamertag is correct first.
        # If it passes, it checks if the gamertag is already in the database.
        # If that passes, we add and commit.

        with db_session:
            if "error" in response:
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

        # Instead of not allowing someone to check the gamertag if they don't have it linked,
        # go ahead and send it as a warning
        with db_session:
            if len(select(g for g in Gamer if g.discord_id == str(ctx.author.id))[:]) == 0:
                await ctx.send("This gamertag isn't linked. If this is your gamertag, use `/setxbox <gamertag>`.")

        response = await gamertag_getter(gamertag=gamertag, game=None, game_variant=None, checker=1)
        
        if "error" in response:
            await ctx.send("I'm sorry, but this gamertag is invalid. Try again with another one.")
        else:    
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

    @commands.command()
    async def latestgame(self, ctx, gamertag = None, game = "All", game_variant = "All"):
        """ Grab latest match stats """

        # Why this long one at the top?
        # First, there is a condition where both arguments can be wrong at the same time.
        # Second, Python runs from the top down (like most languages) so for it to be used, it needs to be at the top.

        # This is a sanity check to make sure the arguments won't make gamertag_getter error out.

        if (game != "All" and game not in CORRECT_GAMES) and (game_variant != "All" and game_variant not in CORRECT_GAME_VARIANT):
            await ctx.send("You need to format the game correctly. Acceptable inputs are: `h1`, `h2`, `h2a`, `h3`, `h4`, `hr`.")
            await ctx.send("You need to format the game variant correctly. Acceptable inputs are: `Slayer`, `CTF`, `Oddball`, `KOTH`, `Juggernaut`, `Infection`, `Flood`, `Race`, `Extraction`, `Dominion`, `Regicide`, `Grifball`, `Ricochet`, `Forge`.")
            return
        elif game != "All" and game not in CORRECT_GAMES:
            await ctx.send("You need to format the game correctly. Acceptable inputs are: `h1`, `h2`, `h2a`, `h3`, `h4`, `hr`.")
            return
        elif game_variant != "All" and game_variant not in CORRECT_GAME_VARIANT:
            await ctx.send("You need to format the game variant correctly. Acceptable inputs are: `Slayer`, `CTF`, `Oddball`, `KOTH`, `Juggernaut`, `Infection`, `Flood`, `Race`, `Extraction`, `Dominion`, `Regicide`, `Grifball`, `Ricochet`, `Forge`.")
            return

        # This is just a warning, it will not stop the function from running, just advises to add it if you haven't already.

        with db_session:
            if len(select(g for g in Gamer if g.discord_id == str(ctx.author.id))[:]) == 0:
                await ctx.send("This gamertag isn't linked. If this is your gamertag, use `/setxbox <gamertag>`.")

        response = await gamertag_getter(gamertag=gamertag, game=game, game_variant=game_variant, checker=2)

        if "error" in response:
            await ctx.send("I'm sorry, but this gamertag is invalid. Try again with another one.")
        else:
            embed = discord.Embed(
                title="Latest Game Stats for Spartan {}".format(gamertag), 
                colour=discord.Colour(0x40cf0f), 
                timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp())
            )

            embed.set_footer(text=f"Requested by {ctx.author.display_name}")

            embed.add_field(name="Game Variant", value=response["games"][0]["gameVariant"], inline=True)
            embed.add_field(name="Map ID", value=response["games"][0]["mapId"], inline=True)
            embed.add_field(name="Won?", value=response["games"][0]["won"], inline=True)
            embed.add_field(name="Score", value=response["games"][0]["score"], inline=True)
            embed.add_field(name="Assists", value=response["games"][0]["assists"], inline=True)
            embed.add_field(name="Kills", value=response["games"][0]["kills"], inline=True)
            embed.add_field(name="Deaths", value=response["games"][0]["deaths"], inline=True)
            embed.add_field(name="Kill/Death Ratio", value=response["games"][0]["killDeathRatio"], inline=True)
            embed.add_field(name="Headshot Rate", value=response["games"][0]["headshotRate"], inline=True)
            embed.add_field(name="Played at...", value=response["games"][0]["playedAtRecency"], inline=True)
            embed.add_field(name="Headshots", value=response["games"][0]["headshots"], inline=True)
            embed.add_field(name="Medals", value=response["games"][0]["medals"], inline=True)        
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MCCStatsAndSquads(bot))