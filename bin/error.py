"""MIT License.

Copyright (c) 2020 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import sys
import traceback
from typing import Coroutine

import discord
from discord.ext import commands


def secondes(num_seconds: int) -> str:
    """Convert a number of seconds in human-readabla format."""
    human_readable = []
    if num_seconds >= 86400:
        human_readable.append(f"{num_seconds//86400} days")
        num_seconds %= 86400
    if num_seconds >= 3600:
        human_readable.append(f"{num_seconds//3600} hours")
        num_seconds %= 3600
    if num_seconds >= 60:
        human_readable.append(f"{num_seconds//60} minutes")
        num_seconds %= 60
    if num_seconds > 0:
        human_readable.append(f"{num_seconds} seconds")
    return ', '.join(human_readable)


async def error_manager(
        ctx: commands.Context,
        error: discord.DiscordException) -> None:
    """Error manager."""
    returned = False
    if isinstance(error, commands.CheckAnyFailure):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            (
                "You don't have the rights to send use the command "
                f"{ctx.invoked_with}"
            ),
        )
    elif isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
        returned = True
        await ctx.bot.httpcat(ctx, 400, str(error))
    elif isinstance(error, commands.MissingRequiredArgument):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            400,
            f"Hmmmm, looks like an argument is missing : {error.param.name}"
        )
    elif isinstance(error, commands.PrivateMessageOnly):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            403,
            "You must be in a private channel to use this command."
        )
    elif isinstance(error, commands.NoPrivateMessage):
        returned = True
        await ctx.bot.httpcat(ctx, 403, "I can't dot this in private.")
    elif isinstance(error, commands.CommandNotFound):
        returned = True
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.bot.httpcat(
            ctx,
            500,
            "Internal error",
            description=(
                "Thank you. My owner is now aware of this bug, which'll"
                " be fixed shortly. (typically, a few minutes "
                "from when he sees it)"
            ),
        )
    elif isinstance(error, commands.DisabledCommand):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            423,
            "Sorry but this command is under maintenance",
        )
    elif isinstance(error, commands.TooManyArguments):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            400,
            "You gave me too many arguments for me to process.",
        )
    elif isinstance(error, commands.CommandOnCooldown):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            429,
            (
                "Calm down, breath and try again in "
                f"{secondes(round(error.retry_after))}"
            ),
        )
    elif isinstance(error, commands.MissingPermissions):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            "\n-".join(
                ["Try again with the following permission(s) :"]
                + error.missing_perms
            ),
        )
    elif isinstance(error, commands.BotMissingPermissions):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            "\n-".join(["I need these permissions :"] + error.missing_perms),
        )
    elif isinstance(error, commands.MissingRole):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            f"Sorry, but you need to be a {error.missing_role}",
        )
    elif isinstance(error, commands.BotMissingRole):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            f"Gimme the role {error.missing_role}, ok ?",
        )
    elif isinstance(error, commands.NSFWChannelRequired):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            403,
            "Woooh ! You must be in an NSFW channel to use this.",
        )
    elif isinstance(error, commands.UnexpectedQuoteError):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            400,
            "I didn't expected that quote...",
        )
    elif isinstance(error, commands.InvalidEndOfQuotedStringError):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            400,
            "You must separate the quoted argument from the others with spaces"
        )
    elif isinstance(error, commands.ExpectedClosingQuoteError):
        returned = True
        await ctx.bot.httpcat(ctx, 400, "I expected a closing quote")
    elif isinstance(error, commands.CheckFailure):
        returned = True
        await ctx.bot.httpcat(
            ctx,
            401,
            "You don't have the rights to use this command",
        )
    else:
        await ctx.bot.httpcat(
            ctx,
            500,
            "The command raised an error",
            description=(
                "Thank you. My owner is now aware of this bug, "
                "which'll be fixed shortly. (typically, a few minutes from "
                "when he sees it)"
            ),
        )

    if returned:
        return

    if not ctx.bot.log_channel:
        raise error

    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    embed = discord.Embed(color=0xFF0000)
    embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))
    embed.title = f"{ctx.author.id} caused an error in {ctx.command}"
    embed.description = f"{type(error).__name__} : {error}"
    if ctx.guild:
        embed.description += (
            f"\nin {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} "
            f"({ctx.channel.id})"
        )
    elif isinstance(ctx.channel, discord.DMChannel):
        embed.description += f"\nin a Private Channel ({ctx.channel.id})"
    else:
        embed.description += (
            f"\nin the Group {ctx.channel.name} ({ctx.channel.id})"
        )
    formatted_traceback = "".join(traceback.format_tb(error.__traceback__))
    embed.description += f"```\n{formatted_traceback}```"
    embed.set_footer(
        text=f"{ctx.bot.user.name} Logging",
        icon_url=ctx.me.avatar_url_as(static_format="png"),
    )
    embed.timestamp = datetime.datetime.utcnow()
    try:
        return await ctx.bot.log_channel.send(embed=embed)
    except discord.DiscordException:
        pass
    await ctx.bot.log_channel.send("Please check the Python logs")
    raise error


def generator(bot: commands.Bot) -> Coroutine:
    """Generate an on_error for the bot."""
    async def predictate(event: str, *args, **kwargs) -> None:
        if event == "on_command_error" or not bot.log_channel:
            raise
        error_type, value, raw_traceback = sys.exc_info()
        embed = discord.Embed(color=0xFF0000)
        embed.title = f"Error in {event} with args {args} {kwargs}"
        embed.description = f"{error_type.__name__} : {value}"
        formatted_traceback = "".join(traceback.format_tb(raw_traceback))
        embed.description += f"```\n{formatted_traceback}```"
        embed.set_footer(
            text=f"{bot.user.name} Logging",
            icon_url=bot.user.avatar_url_as(static_format="png"),
        )
        embed.timestamp = datetime.datetime.utcnow()
        try:
            return await bot.log_channel.send(embed=embed)
        except discord.DiscordException:
            pass
        await bot.log_channel.send("Please check the Python logs")
        raise
    return predictate


def setup(bot: commands.Bot) -> None:
    """Add error managing."""
    bot.add_listener(error_manager, 'on_command_error')
    bot.on_error = generator(bot)
