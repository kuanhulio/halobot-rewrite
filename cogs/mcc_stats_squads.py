import discord
import datetime
import aiohttp
import asyncio
import DiscordUtils

from pony.orm import *
from profanity_check import predict
from discord.ext import commands

BASE_ENDPOINT = "https://halo.api.stdlib.com/mcc@0.1.0/"
STATS_ENDPOINT = "stats/"
GAMES_LATEST_ENDPOINT = "games/latest/"
GAMES_HISTORY_ENDPOINT = "games/history/"

CORRECT_GAMES = ["h1", "h2", "h2a", "h3", "h4", "hr"]

CORRECT_GAME_VARIANT = [
    "Slayer", "CTF", "Oddball", "KOTH", "Juggernaut", "Infection", "Flood",
    "Race", "Extraction", "Dominion", "Regicide", "Grifball", "Ricochet",
    "Forge", "VIP"
]

db = Database()

class Gamer(db.Entity):
    discord_id = Required(str)
    gamertag = Required(str)


class Squads(db.Entity):
    squad_name = Required(str)
    owner_id = Required(str)
    coowner = Optional(str)
    members = Optional(StrArray)
    channel_ids = Required(StrArray)
    role_ids = Required(StrArray)


db.bind(provider='sqlite', filename='xboxusers.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


async def gamertag_getter(gamertag: str,
                          game: str = None,
                          game_variant: str = None,
                          checker: int = 1):
    # This function handles the API calls so my regular functions look nice.
    # Checker = 1 means it's a Stats call
    # Checker = 2 means it's a Latest Game Call
    # TODO: Add more checks if needed.
    if checker == 1:
        params = {"gamertag": gamertag}
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_ENDPOINT + STATS_ENDPOINT,
                                   params=params) as resp:
                returned_value = await resp.json()
            await session.close()
        return returned_value
    elif checker == 2:
        params = {
            "gamertag": gamertag,
            "game": game,
            "gameVariant": game_variant
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_ENDPOINT + GAMES_LATEST_ENDPOINT, params=params) as resp:
                returned_value = await resp.json()
            await session.close()
        return returned_value


@db_session
def setxbox_db(gamertag: str, discord_id: str) -> bool:
    Gamer(discord_id=str(discord_id), gamertag=gamertag)
    commit()
    return True

@db_session
def checkxbox_db(gamertag: str, discord_id: str) -> int:
    if len(select(g for g in Gamer if g.discord_id == discord_id)[:]) == 0:
        return 1
    elif gamertag is not None and len(select(g for g in Gamer if g.gamertag == gamertag)[:]) != 0:
        return 2
    else:
        return 0

@db_session
def xbox_owner(discord_id: str):
    if checkxbox_db(None, discord_id=discord_id) == 1:
        return 1
    else:
        return select(g for g in Gamer if g.discord_id == discord_id)[:][0].gamertag

@db_session
def get_all_squads():
    return select(s for s in Squads)[:]

@db_session
def squad_name_check(potential_squad_name: str):
    if len(select(s for s in Squads if s.squad_name == potential_squad_name)[:]) != 0:
        return 1
    else:
        return 0

@db_session
def squad_owner_check(discord_id: str):
    if len(select(s for s in Squads if s.owner_id == discord_id)[:]) != 0:
        return 1
    else:
        return 0

@db_session
def squad_coowner_check(discord_id: str):
    if len(select(s for s in Squads if s.coowner == discord_id)[:]) != 0:
        return 1
    else:
        return 0
    
@db_session
def squad_coowner_check(discord_id: str):
    if len(select(s for s in Squads if s.coowner == discord_id)[:]) != 0:
        return 1
    else:
        return 0

@db_session
def squad_coowner_check_special(discord_id: str):
    if len(select(s for s in Squads if s.coowner == discord_id)[:]) != 0:
        return 1
    else:
        return 0

@db_session
def squad_member_check(discord_id: str):
    self_squad_member_check = 0
    for x in select(s.members for s in Squads)[:]:
        for member_id in x:
            if discord_id == member_id:
                self_squad_member_check = 1
    
    if self_squad_member_check != 0:
        return 1
    else:
        return 0

@db_session
def get_channel_ids(discord_id: str, owner: bool):
    if owner:
        return select(s for s in Squads if s.owner_id == discord_id)[:][0].channel_ids
    else:
        return select(s for s in Squads if s.coowner == discord_id)[:][0].channel_ids

@db_session
def get_role_ids(discord_id: str, owner: bool):
    if owner:
        return select(s for s in Squads if s.owner_id == discord_id)[:][0].role_ids
    else:
        return select(s for s in Squads if s.coowner == discord_id)[:][0].role_ids

@db_session
def promote_squad(owner: str, discord_id: str):
    select(s for s in Squads if s.owner_id == owner)[:][0].coowner = f"{discord_id}"
    commit()
    return True

@db_session
def demote_squad(owner: str):
    select(s for s in Squads if s.owner_id == owner)[:][0].coowner = ""
    commit()
    return True

@db_session
def create_squad(squad_name: str, owner_id: str, members: list, role_ids: list, channel_ids: list):
    Squads(squad_name=squad_name, owner_id=owner_id, members=members, role_ids=role_ids, channel_ids=channel_ids)
    commit()
    return True

@db_session
def find_squad_by_owner_id(discord_id: str):
    if len(select(s for s in Squads if s.owner_id == discord_id)[:]) == 0:
        return None
    else:
        return select(s for s in Squads if s.owner_id == discord_id)[:][0]

@db_session
def find_squad_by_coowner_id(discord_id: str):
    if len(select(s for s in Squads if s.coowner == discord_id)[:]) == 0:
        return None
    else:
        return select(s for s in Squads if s.coowner == discord_id)[:][0]

@db_session
def delete_squad(discord_id: str):
    select(s for s in Squads if s.owner_id == discord_id)[:][0].delete()
    commit()
    return True

@db_session
def add_member_to_squad(owner_id: str, member_id: str, owner: bool):
    if owner:
        select(s for s in Squads if s.owner_id == owner_id)[:][0].members.append(member_id)
        commit()
        return True
    else:
        select(s for s in Squads if s.coowner == owner_id)[:][0].members.append(member_id)
        commit()
        return True

@db_session
def get_coowner_by_id(discord_id: str):
    return select(s for s in Squads if s.owner_id == discord_id)[:][0].coowner

class MCCStatsAndSquads(commands.Cog):
    """Get your Spartan Stats from the Halo: The Master Chief Collection"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(message_command=False)
    async def setxbox(self, ctx, gamertag: str = commands.Option(description="Set your gamertag to your Discord ID")):
        """ Set your gamertag """

        # This does the client connection to the MCC API.
        # Normally, we'd do OAuth2 auth, but that's too
        # complicated for this adventure.

        response = await gamertag_getter(
            gamertag = gamertag,
            game = None,
            game_variant = None,
            checker = 1
        )

        # This is the first time I have worked with an ORM and a database.
        # This will check if the gamertag is correct first.
        # If it passes, it checks if the gamertag is already in the database.
        # If that passes, we add and commit.
        
        resp = checkxbox_db(gamertag=gamertag, discord_id=str(ctx.author.id))
        
        if "error" in response:
                await ctx.send("I'm sorry, but this gamertag is invalid. Try again with another one.")
        elif resp == 1 or resp == 2:
            await ctx.send("You've already added your gamertag.")
        else:
            setxbox_db(gamertag=gamertag, discord_id=str(ctx.author.id))
            await ctx.send(f"I've set your gamertag to `{gamertag}`!")

    @commands.command(message_command=False)
    async def stats(self, ctx, gamertag = commands.Option(None, description='Grab game stats from a gamertag')):
        """ Grab stats about a Spartan """

        # When working with the database, we have to have this context manager.

        # Instead of not allowing someone to check the gamertag if they don't have it linked,
        # go ahead and send it as a warning

        await ctx.interaction.response.defer()
        
        db_response = xbox_owner(str(ctx.author.id))
        if db_response == 1:
            await ctx.send("This gamertag isn't linked. If this is your gamertag, use `/setxbox <gamertag>`.")
        else:
            gamertag = db_response
            

        response = await gamertag_getter(
            gamertag = gamertag, 
            game = None,
            game_variant = None,
            checker = 1
        )

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

            embed.add_field(
                name="Clantag",
                value=response["clantag"],
                inline=True
            )

            embed.add_field(
                name="Playtime",
                value=response["playtime"],
                inline=True
            )

            embed.add_field(
                name="Games Played",
                value=response["gamesPlayed"],
                inline=True
            )
            
            embed.add_field(
                name="Wins", 
                value=response["wins"], 
                inline=True
            )
            
            embed.add_field(
                name="Losses",
                value=response["losses"],
                inline=True
            )

            embed.add_field(
                name="Win Ratio",            
                value=response["winRatio"],
                inline=True
            )
            
            embed.add_field(
                name="Kills", 
                value=response["kills"], 
                inline=True
            )
            
            embed.add_field(
                name="Deaths",
                value=response["deaths"],
                inline=True
            )

            embed.add_field(
                name="Kill/Death Ratio",
                value=response["killDeathRatio"],
                inline=True
            )
            
            embed.add_field(
                name="Kills Per Game",
                value=response["killsPerGame"],
                inline=True
            )
            
            embed.add_field(
                name="Deaths Per Game",
                value=response["deathsPerGame"],
                inline=True
            )
            
            embed.add_field(
                name="Current Streak",
                value=response["streak"],
                inline=True
            )
            await ctx.interaction.followup.send(embed=embed)

    @commands.command(message_command=False)
    async def latestgame(self, ctx, 
                        gamertag = commands.Option(None, description="Gamertag to search"),
                        game = commands.Option(None, description="Which game to look at"), 
                        game_variant = commands.Option(None, description="Which game variant to look at")):
        """ Grab latest match stats """

        # Why this long one at the top?
        # First, there is a condition where both arguments can be wrong at the same time.
        # Second, Python runs from the top down (like most languages) so for it to be used, it needs to be at the top.

        # This is a sanity check to make sure the arguments won't make gamertag_getter error out.
        
        if game == None:
            game = "All"
        
        if game_variant == None:
            game_variant = "All"

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

        await ctx.interaction.response.defer()

        db_response = xbox_owner(str(ctx.author.id))
        if db_response == 1:
            await ctx.interaction.followup.send("This gamertag isn't linked. If this is your gamertag, use `/setxbox <gamertag>`.")
        else:
            gamertag = db_response

        response = await gamertag_getter(
            gamertag = gamertag, 
            game = game,
            game_variant = game_variant,
            checker = 2
        )

        if "error" in response:
            await ctx.ctx.interaction.followup.send("I'm sorry, but this gamertag is invalid. Try again with another one.")
        else:
            embed = discord.Embed(
                title="Latest Game Stats for Spartan {}".format(gamertag),
                colour=discord.Colour(0x40cf0f),
                timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp())
            )


            embed.set_footer(text=f"Requested by {ctx.author.display_name}")

            embed.add_field(
                name="Game Variant",
                value=response["games"][0]["gameVariant"],
                inline=True
            )

            embed.add_field(
                name="Map ID",
                value=response["games"][0]["mapId"],
                inline=True
            )

            embed.add_field(
                name="Won?", 
                value="Yes" if response["games"][0]["won"] is True else "No", 
                inline=True
            )

            embed.add_field(
                name="Score", 
                value=response["games"][0]["score"], 
                inline=True
            )

            embed.add_field(
                name="Assists",
                value=response["games"][0]["assists"],
                inline=True
            )

            embed.add_field(
                name="Kills", 
                value=response["games"][0]["kills"], 
                inline=True
            )
            
            embed.add_field(
                name="Deaths",
                value=response["games"][0]["deaths"],
                inline=True
            )

            embed.add_field(
                name="Kill/Death Ratio",
                value="{:.3f}".format(response["games"][0]["killDeathRatio"]),
                inline=True
            )
    
            embed.add_field(
                name="Headshot Rate",
                value="{:.0%}".format(response["games"][0]["headshotRate"]),
                inline=True
            )

            embed.add_field(
                name="Played at...",
                value=response["games"][0]["playedAtRecency"],
                inline=True
            )

            embed.add_field(
                name="Headshots",
                value=response["games"][0]["headshots"],
                inline=True
            )

            embed.add_field(
                name="Medals",
                value=response["games"][0]["medals"],
                inline=True
            )

            await ctx.interaction.followup.send(embed=embed)

    @commands.group()
    @commands.guild_only()
    async def squads(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @squads.command(message_command=False, name="list")
    @commands.max_concurrency(1)
    async def _list(self, ctx):
        """ List all the current squads and their rosters """
        embeds = []
        roster = ""

        squads = get_all_squads()

        for squad in squads:
            for gamer in squad.members:
                member = ctx.guild.get_member(int(gamer))
                roster += member.mention + "\n"

            coowner = "No Co-Owner" if squad.coowner == "" else ctx.guild.get_member(int(squad.coowner)).mention

            embed = discord.Embed(
                title="Squad Listings",
                colour=discord.Colour.random(),
                timestamp=datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp())
            )

            embed.add_field(
                name="Squad Name",
                value=f"{squad.squad_name}",
                inline=True
            )

            embed.add_field(
                name="Owner",
                value=f"{ctx.interaction.guild.get_member(int(squad.owner_id)).mention}",
                inline=True
            )

            embed.add_field(
                name="Co-Owner",
                value=f"{coowner}",
                inline=True
            )

            embed.add_field(name="​​​", value="​​", inline=True) # blank for formatting
            embed.add_field(name="Roster", value=f"{roster}", inline=True)
            embed.add_field(name="​​", value="​​", inline=True) # blank for formatting
            embeds.append(embed)
            roster = ""

        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)

    @squads.command(message_command=False)
    async def create(self, ctx, potential_squad_name: str = commands.Option(description="This is the Squad name you want")):
        """Create your own Squad. It requires a name."""

        # So first, we need to make a couple of checks.


        if 1 in predict([potential_squad_name]):
            await ctx.interaction.response.send_message("This is inappropriate. Try again.")
            return
    
        await ctx.interaction.response.defer()

        # Rule 1: You can't have a squad with the same name.
        squad_names_check = squad_name_check(potential_squad_name=potential_squad_name)
        # Rule 2: You can't be in another squad.
        self_squad_owner_check = squad_owner_check(str(ctx.author.id))
        self_squad_coowner_check = squad_coowner_check(str(ctx.author.id))
        self_squad_member_check = squad_member_check(str(ctx.author.id))

        if squad_names_check == 1:
            await ctx.interaction.followup.send("The squad is the same name as another squad. You need to choose another name before you can make a squad.")
        elif self_squad_owner_check == 1:
            await ctx.interaction.followup.send("You own another squad. You need to disband it before you can make a squad.")
        elif self_squad_coowner_check != 0:
            await ctx.interaction.followup.send("You're a co-owner in another squad. You need to leave it before you can make a squad.")
        elif self_squad_member_check != 0:
            await ctx.interaction.followup.send("You're in another squad. You need to leave it before you can make a squad")
        else:
            # Naming our roles and channels
            squad_owner_role_name = potential_squad_name + " Owner"
            squad_coowner_role_name = potential_squad_name + " Co-Owner"
            squad_member_role_name = potential_squad_name + " Member"

            squad_member_channel_name = potential_squad_name + " Chat"
            squad_owner_channel_name = potential_squad_name + " Owner Chat"
            squad_member_voice_channel_name = potential_squad_name + " Chat"

            # Actually making our roles
            SQUADS_CATEGORY_CHANNEL = ctx.interaction.guild.get_channel(894288971314647050)
            SQUAD_OWNER_ROLE = await ctx.interaction.guild.create_role(name=squad_owner_role_name)
            SQUAD_COOWNER_ROLE = await ctx.interaction.guild.create_role(name=squad_coowner_role_name)
            SQUAD_MEMBER_ROLE = await ctx.interaction.guild.create_role(name=squad_member_role_name)

            # Sorting our positions
            positions = {
                SQUAD_OWNER_ROLE: 13,
                SQUAD_COOWNER_ROLE: 13,
                SQUAD_MEMBER_ROLE: 13
            }

            await ctx.interaction.guild.edit_role_positions(positions)

            # Assigning the roles
            await ctx.interaction.user.add_roles(SQUAD_OWNER_ROLE)

            # Create our channels

            member_overwrites = {
                ctx.interaction.guild.default_role: 
                    discord.PermissionOverwrite.from_pair(
                        discord.Permissions.none(), 
                        discord.Permissions.all()
                    ),
                SQUAD_OWNER_ROLE:
                    discord.PermissionOverwrite.from_pair(
                        discord.Permissions.all_channel(),
                        discord.Permissions.none()
                    ),
                SQUAD_COOWNER_ROLE:
                    discord.PermissionOverwrite.from_pair(
                        discord.Permissions.all_channel(),
                        discord.Permissions.none()
                    ),
                SQUAD_MEMBER_ROLE:
                    discord.PermissionOverwrite.from_pair(
                        discord.Permissions.all_channel(),
                        discord.Permissions.none()
                    )
            }

            SQUAD_MEMBER_CHANNEL = await SQUADS_CATEGORY_CHANNEL.create_text_channel(squad_member_channel_name, overwrites=member_overwrites)
            SQUAD_OWNER_CHANNEL = await SQUADS_CATEGORY_CHANNEL.create_text_channel(squad_owner_channel_name, overwrites=member_overwrites)
            SQUAD_VOICE_CHANNEL = await SQUADS_CATEGORY_CHANNEL.create_voice_channel(squad_member_voice_channel_name, overwrites=member_overwrites)

            # Finalize everything for the DB

            roles = [
                str(SQUAD_OWNER_ROLE.id),
                str(SQUAD_COOWNER_ROLE.id),
                str(SQUAD_MEMBER_ROLE.id)
            ]
            channels = [
                str(SQUAD_OWNER_CHANNEL.id),
                str(SQUAD_MEMBER_CHANNEL.id),
                str(SQUAD_VOICE_CHANNEL.id)
            ]
            members = [str(ctx.author.id)]


            create_squad(
                squad_name=potential_squad_name,
                owner_id=str(ctx.author.id),
                members=members,
                role_ids=roles,
                channel_ids=channels
            )

            await ctx.interaction.followup.send("Done! Your squad was made and you have your channels made! Just scroll to find it!")

    @squads.command(message_command=False)
    async def disband(self, ctx):
        """Disbands the Squad. This is an Owner Only command."""

        # We need to do more checks!

        squad = find_squad_by_owner_id(str(ctx.author.id))

        if squad is None:
            await ctx.send("You don't own a squad to disband.")
        else:
            squad_name = squad.squad_name
            squad_role_ids = squad.role_ids
            squad_channel_ids = squad.channel_ids

            for role_id in squad_role_ids:
                role = ctx.interaction.guild.get_role(int(role_id))
                await role.delete()

            for channel_id in squad_channel_ids:
                channel = ctx.interaction.guild.get_channel(int(channel_id))
                await channel.delete()

            await ctx.send(f"`{squad_name}` has been disbanded.")

            delete_squad(discord_id=str(ctx.author.id))

    @squads.command(message_command=False)
    async def invite(self, ctx, member: discord.Member = commands.Option(description='Invite a player to your Squad.')):
        """Invite a player to your Squad! This requires that you're a Co-Owner+."""

        # More checks!
        self_squad_owner_check = squad_owner_check(str(ctx.author.id))
        self_squad_coowner_check = squad_coowner_check(str(ctx.author.id))
        self_squad_member_check = squad_member_check(str(member.id))

        if self_squad_owner_check == 1:
            squad = find_squad_by_owner_id(str(ctx.author.id))
        elif self_squad_coowner_check == 1:
            squad = find_squad_by_coowner_id(str(ctx.author.id))

        
        if (self_squad_owner_check + self_squad_coowner_check == 0) or self_squad_member_check == 1:
            await ctx.send("You do not own or co-own a squad.")
        elif len(squad.members) >= 8:
            await ctx.send("Your Squad is full. You cannot invite this player.")
        else:
            message = await ctx.send(f"{member.mention} has 30 seconds to respond Yes or this invitation will be cancelled!")
            await message.add_reaction("🇾")

            def check_user_positive(reaction, user):
                return user.id == member.id and str(reaction.emoji) == "🇾"

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_user_positive)
            except asyncio.TimeoutError:
                await ctx.send("I'm sorry, but the user either didn't respond in time.")
            else:
                await member.add_roles(ctx.guild.get_role(int(squad.role_ids[2])), reason="Invitation to Squad")
                add_member_to_squad(
                    owner_id=str(ctx.author.id),
                    member_id=str(member.id),
                    owner = True if self_squad_owner_check == 1 else False
                )

                await ctx.send("You've joined the squad! You've been given access to the channels below.")

    @squads.command(message_command=False)
    async def promote(self, ctx, member: discord.Member = commands.Option(description = "Promotes a member to Co-Owner in your Squad.")):
        """Promotes a member in your Squad to Co-Owner! This is Owner Only."""

        self_squad_owner_check = squad_owner_check(str(ctx.author.id))
        self_squad_coowner_check = squad_coowner_check_special(str(ctx.author.id))
        self_squad_member_check = squad_member_check(str(member.id))

        if self_squad_owner_check == 0:
            await ctx.send("You don't own a squad.")
        elif self_squad_member_check == 0:
            await ctx.send(f"{member.mention} is not in your squad.")
        elif self_squad_coowner_check == 0:
            await ctx.send("You already have a co-owner.")
        else:
            await member.add_roles(ctx.guild.get_role(int(get_role_ids(str(ctx.author.id), owner=True)[1])))
            await member.remove_roles(ctx.guild.get_role(int(get_role_ids(str(ctx.author.id), owner=True)[2])))

            promote_squad(owner=str(ctx.author.id), discord_id=member.id)

            await ctx.send(f"You've promoted {member.mention} to co-owner.")

    @squads.command(message_command=False)
    async def demote(self, ctx):
        """Demotes Co-Owner in your Squad to a regular member. This is Owner Only."""

        self_squad_owner_check = squad_owner_check(str(ctx.author.id))
        self_squad_coowner_check = squad_coowner_check_special(str(ctx.author.id))

        if self_squad_owner_check == 0:
            await ctx.send("You don't own a squad.")
        elif self_squad_coowner_check == 1:
            await ctx.send("You don't have a co-owner.")
        else:
            member = ctx.guild.get_member(int(get_coowner_by_id(discord_id=str(ctx.author.id))))
            await member.add_roles(ctx.guild.get_role(int(get_role_ids(str(ctx.author.id), owner=True)[2])))
            await member.remove_roles(ctx.guild.get_role(get_role_ids(str(ctx.author.id), owner=True)[1]))

            demote_squad(owner=str(ctx.author.id))

            await ctx.send(f"You've demoted {member.mention} to co-owner.")

    @squads.command()
    async def remove(self, ctx, member: discord.Member):
        """Removes a person out of the squad. This is Co-Owner+."""

        with db_session:
            self_squad_owner_check = len(
                select(s for s in Squads
                       if s.owner_id == str(ctx.author.id))[:])
            self_squad_coowner_check = len(
                select(s for s in Squads
                       if s.coowner == str(ctx.author.id))[:])
            self_squad_member_check = 0
            for x in select(s.members for s in Squads)[:]:
                for member_id in x:
                    if str(member.id) == member_id:
                        self_squad_member_check = 1

        if self_squad_owner_check == 0 and self_squad_coowner_check.coowner == 0:
            await ctx.send("You don't own a squad.")
        else:
            if self_squad_member_check == 0:
                await ctx.send(f"{member.mention} is not in your squad.")
            else:
                with db_session:
                    if self_squad_owner_check != 0:
                        squad = select(
                            s for s in Squads
                            if s.owner_id == str(ctx.author.id))[:][0]
                        squad.members.remove(str(member.id))
                    else:
                        squad = select(
                            s for s in Squads
                            if s.coowner == str(ctx.author.id))[:][0]
                        squad.members.remove(str(member.id))

                await member.remove_roles(
                    ctx.guild.get_role(int(squad.role_ids[2])))
                await ctx.send(
                    f"{member.mention} has been removed from the squad.")

    @squads.command()
    async def leave(self, ctx):
        """Leaves the squad."""

        with db_session:
            self_squad_coowner_check = len(
                select(s for s in Squads
                       if s.coowner == str(ctx.author.id))[:])
            self_squad_member_check = 0
            for x in select(s.members for s in Squads)[:]:
                for member_id in x:
                    if str(ctx.author.id) == member_id:
                        self_squad_member_check = 1

        if self_squad_member_check == 0 and self_squad_coowner_check == 0:
            await ctx.send("You aren't in a squad.")
        else:
            member = ctx.guild.get_member(ctx.author.id)
            with db_session:
                if self_squad_coowner_check == 1:
                    squad = select(s for s in Squads
                                   if s.coowner == str(ctx.author.id))[:][0]
                    squad.coowner = ""
                    squad.members.remove(str(ctx.author.id))
                    await member.remove_roles(
                        ctx.guild.get_role(int(squad.role_ids[1])))
                else:
                    squad = select(s for s in Squads
                                   if str(ctx.author.id) in s.members)[:][0]
                    squad.members.remove(str(ctx.author.id))
                    await member.remove_roles(
                        ctx.guild.get_role(int(squad.role_ids[2])))

            await ctx.send(f"{member.mention} has left from the squad.")

def setup(bot):
    bot.add_cog(MCCStatsAndSquads(bot))
