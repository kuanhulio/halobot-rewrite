import discord
import re

from discord.ext import commands

SERVER_OWNER_ROLE = 892332617444249600
ADMIN_ROLE = 892329443312406558
MOD_ROLE = 892329626809024542
MUTED_ROLE = 894238129979002920
MOD_LOG_CHANNEL = 892367102789427202


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE, MOD_ROLE)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        for role in member.roles:
            if role in ROLE_LIST:
                SHOULD_CONTINUE
            else:
                continue

        if reason is not None:
            if SHOULD_CONTINUE:
                await member.kick(reason=reason)
                embed = discord.Embed(title="Member Kicked",
                                      colour=discord.Colour.red())

                embed.set_thumbnail(url="{}".format(member.avatar_url))
                embed.set_author(name="Kicked by {}".format(ctx.author.name))

                embed.add_field(name="Member Name",
                                value="{}".format(member.mention))
                embed.add_field(name="User ID", value="{}".format(member.id))
                embed.add_field(name="Reason for Kick",
                                value="{}".format(reason))
                await LOG_CHANNEL.send(embed=embed)
            else:
                await ctx.send(
                    "You tried to kick a fellow admin. Nice one buddy.")
        else:
            await ctx.send("There has to be a reason for the kick.")

    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE, MOD_ROLE)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        try:
            for role in member.roles:
                if role in ROLE_LIST:
                    SHOULD_CONTINUE = False
                else:
                    continue

            if SHOULD_CONTINUE:
                if member.nick is None:
                    nick = member.name
                else:
                    nick = member.nick

                embed = discord.Embed(title="Nickname Change",
                                      colour=discord.Colour.orange())

                embed.set_thumbnail(url="{}".format(member.avatar_url))
                embed.set_author(name="Changed by {}".format(ctx.author.name))

                embed.add_field(name="Old Member Nickname",
                                value="{}".format(nick))
                embed.add_field(name="User ID", value="{}".format(member.id))
                await member.edit(nick=name, reason="Changed by command")
                message = f"Changed **{member.name}'s** nickname to **{name}**"
                if name is None:
                    message = f"Reset **{member.name}'s** nickname"
                await ctx.send(message)
                embed.add_field(name="New Member Nickname",
                                value="{}".format(member.nick))
                await LOG_CHANNEL.send(embed=embed)
            else:
                await ctx.send(
                    "You tried to nickname a fellow admin. Nice one buddy.")

        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """ Bans a user from the current server. """
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        try:
            for role in member.roles:
                if role in ROLE_LIST:
                    SHOULD_CONTINUE = False
                else:
                    continue

            if reason is not None:
                if SHOULD_CONTINUE:
                    await member.ban(reason=reason)
                    embed = discord.Embed(title="Member Banned",
                                          colour=discord.Colour.red())

                    embed.set_thumbnail(url="{}".format(member.avatar_url))
                    embed.set_author(
                        name="Banned by {}".format(ctx.author.name))

                    embed.add_field(name="Member",
                                    value="{}".format(member.mention))
                    embed.add_field(name="User ID",
                                    value="{}".format(member.id))
                    embed.add_field(name="Reason", value="{}".format(reason))
                    await LOG_CHANNEL.send(embed=embed)
                    await ctx.send(
                        f"{member.mention} was banned from the server for `{reason}`."
                    )
                else:
                    await ctx.send(
                        "You tried to ban a fellow admin. Nice one buddy.")
            else:
                await ctx.send("You need to supply a reason.")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.has_any_role(SERVER_OWNER_ROLE)
    async def massban(self, ctx, reason: str = None, *members: discord.Member):
        """ Mass bans multiple members from the server. """
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        try:
            for member_id in members:
                member = ctx.guild.get_member(member_id)
                await ctx.guild.ban(discord.Object(id=member_id),
                                    reason=reason)
                embed = discord.Embed(title="Member Banned",
                                      colour=discord.Colour.red())

                embed.set_thumbnail(url="{}".format(member.avatar_url))
                embed.set_author(name="Banned by {}".format(ctx.author.name))

                embed.add_field(name="Member",
                                value="{}".format(member.mention))
                embed.add_field(name="User ID", value="{}".format(member.id))
                embed.add_field(name="Reason", value="{}".format(reason))
                await LOG_CHANNEL.send(embed=embed)
                await ctx.send(
                    f"{member.mention} was banned from the server for `{reason}`."
                )
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE)
    async def unban(self, ctx, member, *, reason: str = None):
        """ Unbans a user from the current server. """
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)

        try:
            if reason is not None:
                await ctx.guild.unban(discord.Object(id=member), reason=reason)
                embed = discord.Embed(title="Member Unbanned",
                                      colour=discord.Colour.green())

                embed.set_author(name="Unbanned by {}".format(ctx.author.name))

                embed.add_field(name="User ID", value="{}".format(member))
                embed.add_field(name="Reason", value="{}".format(reason))
                await LOG_CHANNEL.send(embed=embed)
                await ctx.send(
                    f"{member} was unbanned from the server for `{reason}`.")
            else:
                await ctx.send("You need to supply a reason.")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE, MOD_ROLE)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        muted_role = ctx.guild.get_role(MUTED_ROLE)
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        try:
            for role in member.roles:
                if role in ROLE_LIST:
                    SHOULD_CONTINUE = False
                else:
                    continue

            if reason is not None:
                if SHOULD_CONTINUE:
                    await member.add_roles(muted_role, reason=reason)
                    embed = discord.Embed(title="Member Muted",
                                          colour=discord.Colour.orange())

                    embed.set_thumbnail(url="{}".format(member.avatar_url))
                    embed.set_author(
                        name="Muted by {}".format(ctx.author.name))

                    embed.add_field(name="Member",
                                    value="{}".format(member.mention))
                    embed.add_field(name="User ID",
                                    value="{}".format(member.id))
                    embed.add_field(name="Reason", value="{}".format(reason))
                    await LOG_CHANNEL.send(embed=embed)
                    await ctx.send(
                        f"{member.mention} was muted in the server for `{reason}`."
                    )
                else:
                    await ctx.send(
                        "You tried to mute a fellow admin. Nice one buddy.")
            else:
                await ctx.send("You need to supply a reason.")

        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE, MOD_ROLE)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        muted_role = ctx.guild.get_role(MUTED_ROLE)
        ROLE_LIST = [
            ctx.guild.get_role(SERVER_OWNER_ROLE),
            ctx.guild.get_role(ADMIN_ROLE),
            ctx.guild.get_role(MOD_ROLE)
        ]
        LOG_CHANNEL = ctx.guild.get_channel(MOD_LOG_CHANNEL)
        SHOULD_CONTINUE = True

        try:
            for role in member.roles:
                if role in ROLE_LIST:
                    SHOULD_CONTINUE = False
                else:
                    continue

            if reason is not None:
                if SHOULD_CONTINUE:
                    await member.remove_roles(muted_role, reason=reason)
                    embed = discord.Embed(title="Member Unmuted",
                                          colour=discord.Colour.orange())

                    embed.set_thumbnail(url="{}".format(member.avatar_url))
                    embed.set_author(
                        name="Unmuted by {}".format(ctx.author.name))

                    embed.add_field(name="Member",
                                    value="{}".format(member.mention))
                    embed.add_field(name="User ID",
                                    value="{}".format(member.id))
                    embed.add_field(name="Reason", value="{}".format(reason))
                    await LOG_CHANNEL.send(embed=embed)
                    await ctx.send(
                        f"{member.mention} was unmuted in the server for `{reason}`."
                    )
                else:
                    await ctx.send(
                        "You tried to mute a fellow admin. Nice one buddy.")
            else:
                await ctx.send("You need to supply a reason.")

        except Exception as e:
            await ctx.send(e)

    @commands.group()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.has_any_role(SERVER_OWNER_ROLE, ADMIN_ROLE, MOD_ROLE)
    async def prune(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def do_removal(self,
                         ctx,
                         limit,
                         predicate,
                         *,
                         before=None,
                         after=None,
                         message=True):
        if limit > 2000:
            return await ctx.send(
                f'Too many messages to search given ({limit}/2000)')

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit,
                                              before=before,
                                              after=after,
                                              check=predicate)
        except discord.Forbidden:
            return await ctx.send(
                'I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        deleted = len(deleted)
        if message is True:
            await ctx.send(
                f'🚮 Successfully removed {deleted} message{"" if deleted == 1 else "s"}.'
            )

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def mentions(self, ctx, search=100):
        """Removes messages that have mentions in them."""
        await self.do_removal(
            ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search,
                              lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send(
                'The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name='bots')
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = prefix if prefix else self.config["prefix"]

        def predicate(m):
            return (m.webhook_id is None
                    and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='users')
    async def _users(self, ctx, prefix=None, search=100):
        """Removes only user messages. """
        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='emojis')
    async def _emojis(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(
            r'<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(
                f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')


def setup(bot):
    bot.add_cog(Moderator(bot))
