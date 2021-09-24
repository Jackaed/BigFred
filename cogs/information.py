from datetime import datetime

import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    def info_embed(self, on: str, title: str = "", colour: discord.Colour = discord.Colour.green(), author: discord.User = None):
        embed = discord.Embed(title=title,
                              colour=colour,
                              description=f"Information on `{on}` at `{self.fred_functions.date(datetime.now())}`")

        if author:
            embed.set_author(name=author.display_name, icon_url=author.avatar_url)

        return embed

    @commands.command(aliases=["u"])
    async def user(self, ctx: commands.Context, user=None):
        if user is None:
            member = ctx.author
        else:
            member = ctx.message.mentions[0]

        user_info = f"**Created:** `{self.fred_functions.date(member.created_at)}`\n"
        user_info += f"**Age:** `{str(datetime.now() - member.created_at).split('.')[0]}`\n"
        user_info += f"**ID:** `{member.id}`\n"
        user_info += f"**Status:** `{'Do Not Disturb' if str(member.status) == 'dnd' else str(member.status).title()}`\n"
        if member.activity:
            user_info += f"**Activity:** `{member.activity.name}`\n"
        else:
            user_info += f"**Activity:** `None`\n"
        user_info += f"**Pending:** `{'Yes' if member.pending else 'No'}`\n"

        roles = member.roles
        roles.reverse()
        guild_info = f"**Roles ({len(roles) - 1}):** {' '.join([s.mention for s in roles if not s.is_default()])}\n"
        guild_info += f"**Nickname:** `{member.nick}`\n"
        guild_info += f"**Joined:** `{self.fred_functions.date(member.joined_at)}`\n"
        guild_info += f"**In server:** `{str(datetime.now() - member.joined_at).split('.')[0]}`"

        embed = self.info_embed(member.display_name)

        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.add_field(name=f"Information ({member.guild.name})", value=guild_info, inline=True)
        embed.add_field(name=f"Information ({member.display_name})", value=user_info, inline=True)

        await ctx.reply(embed=embed)

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: commands.Context, user=None):
        if user is None:
            member = ctx.author
        else:
            member = ctx.message.mentions[0]

        embed = self.info_embed(f"{member.display_name}'s Avatar")

        embed.set_author(name=str(member))
        embed.set_image(url=member.avatar_url)

        await ctx.reply(embed=embed)

    @commands.command(aliases=["role"])
    async def roles(self, ctx: commands.Context, user=None):
        member = None
        roles = []

        if user is None:
            member = ctx.author
        elif len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
        elif len(ctx.message.role_mentions) > 0:
            roles = ctx.message.role_mentions

        if member is not None:
            roles += [r for r in member.roles if r.hoist]
            roles.reverse()

        if len(ctx.message.role_mentions) > 0:
            roles = ctx.message.role_mentions

        roles: [discord.Role]
        for role in roles:
            role: discord.Role

            embed = self.info_embed(role.name, title=role.name, colour=role.colour)

            if len(role.members) > 50:
                shown_members = role.members[:50]
            else:
                shown_members = role.members

            embed.add_field(name=f"Members ({len(shown_members)}/{len(role.members)}):",
                            value=' '.join([m.mention for m in shown_members]))

            info = f"**Colour:** `{str(role.colour).upper()}`\n"
            info += f"**Created:** `{self.fred_functions.date(role.created_at)}`\n"
            info += f"**Age:** `{datetime.now() - role.created_at}`\n"
            info += f"**Displayed Separately:** `{'Yes' if role.hoist else 'No'}`\n"
            info += f"**ID:** `{role.id}`"
            embed.add_field(name="Information", value=info)

            await ctx.reply(embed=embed)

    @commands.command(aliases=["chan"])
    async def channel(self, ctx: commands.Context):
        if len(ctx.message.channel_mentions) > 0:
            channels = ctx.message.channel_mentions
        else:
            channels = [ctx.channel]

        for channel in channels:
            channel: discord.TextChannel

            embed = self.info_embed(channel.name, title=channel.name)

            members = [m.mention for m in channel.members if not m.bot]
            bots = [m.mention for m in channel.members if m.bot]

            info = f"**Created:** `{self.fred_functions.date(channel.created_at)}`\n"
            info += f"**Age:** `{datetime.now() - channel.created_at}`\n"
            info += f"**Members ({len(members)}):** {(' '.join(members[:30]))} {f'+{len(members) - 30} more' if len(members) > 30 else ''}\n"
            info += f"**Bots ({len(bots)}):** {' '.join(bots)}\n"
            info += f"**ID:** `{channel.id}`\n"
            info += f"**Topic:** `{channel.topic}`\n"
            info += f"**NSFW:** `{'yes' if channel.nsfw else 'no'}`\n"
            info += f"**Category:** `{channel.category}`"

            embed.add_field(name="Information", value=info)

            await ctx.reply(embed=embed)

    @commands.command(aliases=["guild"])
    async def server(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild

        embed = self.info_embed(on=guild.name, title=guild.name)

        embed.set_thumbnail(url=guild.icon_url)

        members = [m.mention for m in guild.members if not m.bot]
        bots = [m.mention for m in guild.members if m.bot]

        info = f"**Created:** `{self.fred_functions.date(guild.created_at)}`\n"
        info += f"**Age:** `{datetime.now() - guild.created_at}`\n"
        info += f"**Members ({len(members)}):** {(' '.join(members[:30]))} {f'+{len(members) - 30} more' if len(members) > 30 else ''}\n"
        info += f"**Bots ({len(bots)}):** {' '.join(bots)}\n"
        info += f"**ID:** `{guild.id}`"

        embed.add_field(name="Information", value=info)

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Information(bot))
