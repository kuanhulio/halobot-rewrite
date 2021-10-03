import discord

from datetime import datetime
from discord.ext import commands

ALL_USER_VC_COUNTER    = 893573851584290816
ALL_CHANNEL_VC_COUNTER = 893573912183603222
ALL_ROLE_VC_COUNTER    = 893573978285809764

STAFF_RANKS_SPACER     = 892327566323613706
CONSOLE_RANKS_SPACER   = 892345177480499220
GAME_RANKS_SPACER      = 892328071649165343
PERMISSIONS_SPACER     = 892328268668219392

EASY_LURKER_ROLE       = 892332958650884148
NORMAL_PLAYER_ROLE     = 892332896092839937

HALO_CE_EMOTE          = 892341519296651284
HALO_2_EMOTE           = 892341690902409216
HALO_3_EMOTE           = 892341779792289794
HALO_3_ODST_EMOTE      = 893031684205871184
HALO_REACH_EMOTE       = 892354416643014667
HALO_4_EMOTE           = 892341983006294048
HALO_5_EMOTE           = 892352410796838912
HALO_INFINITE_EMOTE    = 892342791080927272
HALO_WARS_EMOTE        = 892350297043783681
HALO_WARS_2_EMOTE      = 892350429252423771
HALO_ASSAULT_EMOTE     = 892353849069826070
HALO_STRIKE_EMOTE      = 892352127026987018

CAMPAIGN_EMOTE         = 893212828629086279
MULTIPLAYER_EMOTE      = 893213063841472562
FIREFIGHT_EMOTE        = 893213324769108039
CUSTOMS_EMOTE          = 893213809379004446
FORGE_EMOTE            = 893214151101538324

XBOX_ONE_EMOTE         = 893210651936317510
XBOX_SERIES_EMOTE      = 893211092069781514
PC_EMOTE               = 893210773357215765

ROLE_MESSAGE_ID        = 893214480249540668
MOD_LOG_CHANNEL_ID     = 892367102789427202

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        await self.bot.change_presence(
            activity=discord.Game("with the test subjects."),
            status=discord.Status.online
        )

        update_user_channel = discord.utils.get(self.bot.get_all_channels(), id=ALL_USER_VC_COUNTER)
        await update_user_channel.edit(name="All Members: {}".format(update_user_channel.guild.member_count))

        update_role_channel = discord.utils.get(self.bot.get_all_channels(), id=ALL_ROLE_VC_COUNTER)
        await update_role_channel.edit(name="Roles Count: {}".format(len(update_role_channel.guild.roles)))

        update_channel = discord.utils.get(self.bot.get_all_channels(), id=ALL_CHANNEL_VC_COUNTER)
        await update_channel.edit(name="Channels Count: {}".format(len(update_role_channel.guild.channels)))

        # Indicate that the bot has successfully booted up
        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        update_user_channel = discord.utils.get(self.bot.get_all_channels(), id=ALL_USER_VC_COUNTER)
        MOD_LOG_CHANNEL = member.guild.get_channel(MOD_LOG_CHANNEL_ID)
        STAFF_RANKS = member.guild.get_role(STAFF_RANKS_SPACER)
        CONSOLE_RANKS = member.guild.get_role(CONSOLE_RANKS_SPACER)
        PERMISSIONS_RANKS_SPACER = member.guild.get_role(PERMISSIONS_SPACER)
        GAME_RANKS = member.guild.get_role(GAME_RANKS_SPACER)
        EASY_LURKER = member.guild.get_role(EASY_LURKER_ROLE)
        await member.add_roles(STAFF_RANKS, reason="New User Join")
        await member.add_roles(CONSOLE_RANKS, reason="New User Join")
        await member.add_roles(PERMISSIONS_RANKS_SPACER, reason="New User Join")
        await member.add_roles(GAME_RANKS, reason="New User Join")        
        await member.add_roles(EASY_LURKER, reason="New User Join")
        await update_user_channel.edit(name="All Members: {}".format(update_user_channel.guild.member_count))

        embed = discord.Embed(title="Member Join", colour=discord.Colour.green(), description="This is posted when a new member joins the Guild.")
        embed.set_thumbnail(url="{}".format(member.avatar_url))
        embed.set_author(name="{}".format(member.name), icon_url="{}".format(member.avatar_url))

        embed.add_field(name="Player Name", value="{}".format(member.mention))
        embed.add_field(name="Created Account At", value="{}".format(member.created_at))
        embed.add_field(name="User ID", value="{}".format(member.id))
        embed.add_field(name="Joined Guild At", value="{}".format(member.joined_at))
        await MOD_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        MOD_LOG_CHANNEL = message.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Message Deleted", colour=discord.Colour.red(), description="This is posted when a message gets deleted.")

        embed.set_thumbnail(url="{}".format(message.author.avatar_url))
        embed.set_author(name="{}".format(message.author.name), icon_url="{}".format(message.author.avatar_url))

        embed.add_field(name="Message Deleted", value="{}".format(message.clean_content))
        embed.add_field(name="User ID", value="{}".format(message.author.id))
        embed.add_field(name="Posted at", value="{}".format(message.created_at))
        await MOD_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        MOD_LOG_CHANNEL = before.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Message Edited", colour=discord.Colour.orange(), description="This is posted when a message gets edited.")

        embed.set_thumbnail(url="{}".format(before.author.avatar_url))
        embed.set_author(name="{}".format(before.author.name), icon_url="{}".format(before.author.avatar_url))

        embed.add_field(name="Message Before Edit", value="{}".format(before.clean_content))
        embed.add_field(name="Message After Edit", value="{}".format(after.clean_content))
        embed.add_field(name="User ID", value="{}".format(before.author.id))
        embed.add_field(name="Originally Posted at", value="{}".format(before.created_at))
        embed.add_field(name="Edited At", value="{}".format(after.edited_at))
        await MOD_LOG_CHANNEL.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        reaction = payload

        NORMAL_PLAYER = reaction.member.guild.get_role(NORMAL_PLAYER_ROLE)
        EASY_LURKER   = reaction.member.guild.get_role(EASY_LURKER_ROLE)

        HALO_CE       = reaction.member.guild.get_role(892330097665769495)
        HALO_2        = reaction.member.guild.get_role(892331777136394270)
        HALO_3        = reaction.member.guild.get_role(892331825584803850)
        HALO_3_ODST   = reaction.member.guild.get_role(892345849881976833)
        HALO_REACH    = reaction.member.guild.get_role(892345774229303326)
        HALO_4        = reaction.member.guild.get_role(892331846606659626)
        HALO_5        = reaction.member.guild.get_role(892348735642800149)
        HALO_INFINITE = reaction.member.guild.get_role(892331937111363645)
        HALO_WARS     = reaction.member.guild.get_role(892348956724580352)
        HALO_WARS_2   = reaction.member.guild.get_role(892349656791674900)
        HALO_ASSAULT  = reaction.member.guild.get_role(892349492383318016)
        HALO_STRIKE   = reaction.member.guild.get_role(892349571294978078)

        CAMPAIGN      = reaction.member.guild.get_role(892346977000513556)
        MULTIPLAYER   = reaction.member.guild.get_role(892347051323588648)
        FIREFIGHT     = reaction.member.guild.get_role(892347094013181973)
        CUSTOMS       = reaction.member.guild.get_role(892347124849717258)
        FORGE         = reaction.member.guild.get_role(892347153236770817)

        XBOX_ONE      = reaction.member.guild.get_role(892345337602244628)
        XBOX_SERIES   = reaction.member.guild.get_role(892345369814503454)
        PC            = reaction.member.guild.get_role(892345473854230548)

        # EVENTS        = reaction.member.guild.get_role(824458534372114532)

        if reaction.message_id == ROLE_MESSAGE_ID:
            if reaction.emoji.id == HALO_CE_EMOTE:
                await reaction.member.add_roles(HALO_CE)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_2_EMOTE:
                await reaction.member.add_roles(HALO_2)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_3_EMOTE:
                await reaction.member.add_roles(HALO_3)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_3_ODST_EMOTE:
                await reaction.member.add_roles(HALO_3_ODST)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_REACH_EMOTE:
                await reaction.member.add_roles(HALO_REACH)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_4_EMOTE:
                await reaction.member.add_roles(HALO_4)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_5_EMOTE:
                await reaction.member.add_roles(HALO_5)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_INFINITE_EMOTE:
                await reaction.member.add_roles(HALO_INFINITE)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_WARS_EMOTE:
                await reaction.member.add_roles(HALO_WARS)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_WARS_2_EMOTE:
                await reaction.member.add_roles(HALO_WARS_2)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_ASSAULT_EMOTE:
                await reaction.member.add_roles(HALO_ASSAULT)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == HALO_STRIKE_EMOTE:
                await reaction.member.add_roles(HALO_STRIKE)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == CAMPAIGN_EMOTE:
                await reaction.member.add_roles(CAMPAIGN)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == MULTIPLAYER_EMOTE:
                await reaction.member.add_roles(MULTIPLAYER)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == FIREFIGHT_EMOTE:
                await reaction.member.add_roles(FIREFIGHT)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == CUSTOMS_EMOTE:
                await reaction.member.add_roles(CUSTOMS)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == FORGE_EMOTE:
                await reaction.member.add_roles(FORGE)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == XBOX_ONE_EMOTE:
                await reaction.member.add_roles(XBOX_ONE)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == XBOX_SERIES_EMOTE:
                await reaction.member.add_roles(XBOX_SERIES)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)
            if reaction.emoji.id == PC_EMOTE:
                await reaction.member.add_roles(PC)
                if NORMAL_PLAYER not in reaction.member.roles:
                    await reaction.member.add_roles(NORMAL_PLAYER)
                    await reaction.member.remove_roles(EASY_LURKER)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        reaction = payload

        HALO_CE       = guild.get_role(892330097665769495)
        HALO_2        = guild.get_role(892331777136394270)
        HALO_3        = guild.get_role(892331825584803850)
        HALO_3_ODST   = guild.get_role(892345849881976833)
        HALO_REACH    = guild.get_role(892345774229303326)
        HALO_4        = guild.get_role(892331846606659626)
        HALO_5        = guild.get_role(892348735642800149)
        HALO_INFINITE = guild.get_role(892331937111363645)
        HALO_WARS     = guild.get_role(892348956724580352)
        HALO_WARS_2   = guild.get_role(892349656791674900)
        HALO_ASSAULT  = guild.get_role(892349492383318016)
        HALO_STRIKE   = guild.get_role(892349571294978078)

        CAMPAIGN      = guild.get_role(892346977000513556)
        MULTIPLAYER   = guild.get_role(892347051323588648)
        FIREFIGHT     = guild.get_role(892347094013181973)
        CUSTOMS       = guild.get_role(892347124849717258)
        FORGE         = guild.get_role(892347153236770817)

        XBOX_ONE      = guild.get_role(892345337602244628)
        XBOX_SERIES   = guild.get_role(892345369814503454)
        PC            = guild.get_role(892345473854230548)

        # EVENTS        = guild.get_role(824458534372114532)

        if reaction.message_id == ROLE_MESSAGE_ID:
            if reaction.emoji.id == HALO_CE_EMOTE:
                await member.remove_roles(HALO_CE)
            if reaction.emoji.id == HALO_2_EMOTE:
                await member.remove_roles(HALO_2)               
            if reaction.emoji.id == HALO_3_EMOTE:
                await member.remove_roles(HALO_3)                
            if reaction.emoji.id == HALO_3_ODST_EMOTE:
                await member.remove_roles(HALO_3_ODST)                
            if reaction.emoji.id == HALO_REACH_EMOTE:
                await member.remove_roles(HALO_REACH)               
            if reaction.emoji.id == HALO_4_EMOTE:
                await member.remove_roles(HALO_4)            
            if reaction.emoji.id == HALO_5_EMOTE:
                await member.remove_roles(HALO_5)           
            if reaction.emoji.id == HALO_INFINITE_EMOTE:
                await member.remove_roles(HALO_INFINITE)       
            if reaction.emoji.id == HALO_WARS_EMOTE:
                await member.remove_roles(HALO_WARS)              
            if reaction.emoji.id == HALO_WARS_2_EMOTE:
                await member.remove_roles(HALO_WARS_2)     
            if reaction.emoji.id == HALO_ASSAULT_EMOTE:
                await member.remove_roles(HALO_ASSAULT)        
            if reaction.emoji.id == HALO_STRIKE_EMOTE:
                await member.remove_roles(HALO_STRIKE)
            if reaction.emoji.id == CAMPAIGN_EMOTE:
                await member.remove_roles(CAMPAIGN)
            if reaction.emoji.id == MULTIPLAYER_EMOTE:
                await member.remove_roles(MULTIPLAYER)                
            if reaction.emoji.id == FIREFIGHT_EMOTE:
                await member.remove_roles(FIREFIGHT)                
            if reaction.emoji.id == CUSTOMS_EMOTE:
                await member.remove_roles(CUSTOMS)
            if reaction.emoji.id == FORGE_EMOTE:
                await member.remove_roles(FORGE)
            if reaction.emoji.id == XBOX_ONE_EMOTE:
                await member.remove_roles(XBOX_ONE)
            if reaction.emoji.id == XBOX_SERIES_EMOTE:
                await member.remove_roles(XBOX_SERIES)
            if reaction.emoji.id == PC_EMOTE:
                await member.remove_roles(PC)

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        if message.author.bot:
            return

        channel = message.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Reactions Cleared", colour=discord.Colour.orange(), description="This is posted when a message's reactions are cleared.")

        embed.set_thumbnail(url="{}".format(message.author.avatar_url))
        embed.set_author(name="{}".format(message.author.name), icon_url="{}".format(message.author.avatar_url))

        embed.add_field(name="Message Content", value="{}".format(message.clean_content))
        embed.add_field(name="User ID", value="{}".format(message.author.id))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        mod_channel = channel.guild.get_channel(MOD_LOG_CHANNEL_ID)

        embed = discord.Embed(title="Channel Created", colour=discord.Colour.green(), description="This is posted when a Channel gets made.")
        embed.add_field(name="Channel Name", value="{}".format(channel.mention))
        embed.add_field(name="Channel ID", value="{}".format(channel.id))
        await mod_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        mod_channel = channel.guild.get_channel(MOD_LOG_CHANNEL_ID)

        embed = discord.Embed(title="Channel Deleted", colour=discord.Colour.red(), description="This is posted when a Channel gets deleted.")
        embed.add_field(name="Channel Name", value="{}".format(channel.name))
        embed.add_field(name="Channel ID", value="{}".format(channel.id))
        await mod_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        if member.author.bot:
            return

        update_user_channel = discord.utils.get(self.bot.get_all_channels(), id=ALL_USER_VC_COUNTER)
        channel = member.guild.get_channel(MOD_LOG_CHANNEL_ID)

        await update_user_channel.edit(name="All Members: {}".format(update_user_channel.guild.member_count))
        embed = discord.Embed(title="Member Left", colour=discord.Colour.red(), description="This is posted when a member leaves the Guild.")

        embed.set_thumbnail(url="{}".format(member.avatar_url))
        embed.set_author(name="{}".format(member.name), icon_url="{}".format(member.avatar_url))

        embed.add_field(name="Player Name", value="{}".format(member.mention))
        embed.add_field(name="User ID", value="{}".format(member.id))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.bot:
            return

        channel = before.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="User Profile Changed", colour=discord.Colour.orange(), description="This is posted when a member edits their profile.")

        embed.set_thumbnail(url="{}".format(before.avatar_url))
        embed.set_author(name="{}".format(before.name), icon_url="{}".format(before.avatar_url))

        embed.add_field(name="Old Avatar", value="{}".format(before.avatar))
        embed.add_field(name="Old Username", value="{}".format(before.name))
        embed.add_field(name="Old Discriminator", value="{}".format(before.discriminator))
        embed.add_field(name="New Avatar", value="{}".format(after.avatar))
        embed.add_field(name="New Username", value="{}".format(after.name))
        embed.add_field(name="New Discriminator", value="{}".format(after.discriminator))
        embed.add_field(name="User ID", value="{}".format(before.id))
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.author.bot:
            return

        channel = before.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="User Profile Changed", colour=discord.Colour.green(), description="This is posted when a member edits their profile.")

        embed.set_thumbnail(url="{}".format(before.avatar_url))
        embed.set_author(name="{}".format(before.name), icon_url="{}".format(before.avatar_url))

        embed.add_field(name="Old Avatar", value="{}".format(before.avatar))
        embed.add_field(name="Old Username", value="{}".format(before.name))
        embed.add_field(name="Old Discriminator", value="{}".format(before.discriminator))
        embed.add_field(name="New Avatar", value="{}".format(after.avatar))
        embed.add_field(name="New Username", value="{}".format(after.name))
        embed.add_field(name="New Discriminator", value="{}".format(after.discriminator))
        embed.add_field(name="User ID", value="{}".format(before.id))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if user.bot:
            return

        channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Member Banned", colour=discord.Colour.red(), description="This is posted when a member is banned.")

        embed.set_thumbnail(url="{}".format(user.avatar_url))
        embed.set_author(name="{}".format(user.name))

        embed.add_field(name="Avatar", value="{}".format(user.avatar_url))
        embed.add_field(name="Username", value="{}".format(user.name))
        embed.add_field(name="User ID", value="{}".format(user.id))
        embed.add_field(name="Created Account At", value="{}".format(user.created_at))

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        if member.bot:
            return

        channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Member Unbanned", colour=discord.Colour.green(), description="This is posted when a member is unbanned.")

        embed.set_thumbnail(url="{}".format(member.avatar_url))
        embed.set_author(name="{}".format(member.name))

        embed.add_field(name="Avatar", value="{}".format(member.avatar_url))
        embed.add_field(name="Username", value="{}".format(member.name))
        embed.add_field(name="User ID", value="{}".format(member.id))
        embed.add_field(name="Created Account At", value="{}".format(member.created_at))

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        member = invite.inviter

        channel = invite.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Invite Created", colour=discord.Colour.green(), description="This is posted when a invite is created.")

        embed.set_thumbnail(url="{}".format(member.avatar_url))
        embed.set_author(name="{}".format(member.name))

        embed.add_field(name="Invite ID", value="{}".format(invite.id))
        embed.add_field(name="Invite Code", value="{}".format(invite.code))
        embed.add_field(name="Invite Created At", value="{}".format(invite.created_at))
        embed.add_field(name="Avatar", value="{}".format(member.avatar_url))
        embed.add_field(name="Username", value="{}".format(member.name))
        embed.add_field(name="User ID", value="{}".format(member.id))
        embed.add_field(name="Created Account At", value="{}".format(member.created_at))

        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        member = invite.inviter

        channel = invite.guild.get_channel(MOD_LOG_CHANNEL_ID)
        embed = discord.Embed(title="Invite Deleted", colour=discord.Colour.green(), description="This is posted when a invite is deleted.")

        embed.set_thumbnail(url="{}".format(member.avatar_url))
        embed.set_author(name="{}".format(member.name))

        embed.add_field(name="Invite ID", value="{}".format(invite.id))
        embed.add_field(name="Invite Code", value="{}".format(invite.code))
        embed.add_field(name="Invite Created At", value="{}".format(invite.created_at))
        embed.add_field(name="Avatar", value="{}".format(member.avatar_url))
        embed.add_field(name="Username", value="{}".format(member.name))
        embed.add_field(name="User ID", value="{}".format(member.id))
        embed.add_field(name="Created Account At", value="{}".format(member.created_at))

        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))