"""MIT License

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
SOFTWARE."""

import pickle
import traceback
from discord.ext import commands
import discord
import datetime

from os import path

def secondes(s):
    r=[]
    if s>=86400:
        r.append(str(s//86400)+' days')
        s%=86400
    if s>=3600:
        r.append(str(s//3600)+' hours')
        s%=3600
    if s>=60:
        r.append(str(s//60)+' minutes')
        s%=60
    if s>0:
        r.append(str(s)+' seconds')
    return ', '.join(r)

async def error_manager(ctx,error):
    '''Error manager'''
    if isinstance(error,commands.CheckAnyFailure):
        await ctx.bot.httpcat(ctx,401,"You don't have the rights to send use the command "+ctx.invoked_with)
    elif isinstance(error,(commands.BadArgument,commands.BadUnionArgument)):
        await ctx.bot.httpcat(ctx,400,str(error))
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.bot.httpcat(ctx,400,"Hmmmm, looks like an argument is missing : "+error.param.name)
    elif isinstance(error,commands.PrivateMessageOnly):
        await ctx.bot.httpcat(ctx,403,"You must be in a private channel to use this command.")
    elif isinstance(error,commands.NoPrivateMessage):
        await ctx.bot.httpcat(ctx,403,"I can't dot this in private.")
    elif isinstance(error,commands.CommandNotFound):
        await ctx.bot.httpcat(ctx,404)
    elif isinstance(error,commands.CommandInvokeError):
        await ctx.bot.httpcat(ctx,500,str(error))
    elif isinstance(error,commands.DisabledCommand):
        await ctx.bot.httpcat(ctx,423,'God said : this command is disabled. So it is.')
    elif isinstance(error,commands.TooManyArguments):
        await ctx.bot.httpcat(ctx,400,"You gave me too much arguments for me to process.")
    elif isinstance(error,commands.CommandOnCooldown):
        await ctx.bot.httpcat(ctx,429,'Calm down, breath and try again in '+secondes(round(error.retry_after)))
    elif isinstance(error,commands.MissingPermissions):
        await ctx.bot.httpcat(ctx,401,'\n-'.join(['Try again with the following permission(s) :']+error.missing_perms))
    elif isinstance(error,commands.BotMissingPermissions):
        await ctx.bot.httpcat(ctx,401,'\n-'.join(["I need these permissions :"]+error.missing_perms))
    elif isinstance(error,commands.MissingRole):
        await ctx.bot.httpcat(ctx,401,"Sorry, but you need to be a "+str(error.missing_role))
    elif isinstance(error,commands.BotMissingRole):
        await ctx.bot.httpcat(ctx,401,"Gimme the role "+str(error.missing_role)+" first, ok ?")
    elif isinstance(error,commands.NSFWChannelRequired):
        await ctx.bot.httpcat(ctx,403,"Woooh ! You must be in an NSFW channel to use this.")
    elif isinstance(error,commands.UnexpectedQuoteError):
        await ctx.bot.httpcat(ctx,400,"I didn't expected that quote...")
    elif isinstance(error,commands.InvalidEndOfQuotedStringError):
        await ctx.bot.httpcat(ctx,400,"You must separated the quoted argument from the others with spaces")
    elif isinstance(error,commands.ExpectedClosingQuoteError):
        await ctx.bot.httpcat(ctx,400,"I expected a closing quote")
    elif isinstance(error,commands.CheckFailure):
        await ctx.bot.httpcat(ctx,401,"You don't have the rights to use this command")
    else:
        await ctx.bot.httpcat(ctx,500,'The command raised an error')

    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.UserInputError) or isinstance(error, commands.CheckFailure) or isinstance(error, commands.DisabledCommand) or isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.MaxConcurrencyReached):
        return
    if isinstance(error,commands.CommandInvokeError):
        error=error.original
    embed = discord.Embed(color=0xFF0000)
    embed.title = f"{ctx.author} ({ctx.author.id}) caused an error in {ctx.command} ({type(error).__name__})"
    if ctx.guild:
        embed.description = f"in {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} ({ctx.channel.id})"
    elif isinstance(ctx.channel,discord.DMChannel):
        embed.description = f"in a Private Channel ({ctx.channel.id})"
    else:
        embed.description = f"in the Group {ctx.channel.name} ({ctx.channel.id})"
    tb = "".join(traceback.format_tb(error.__traceback__))
    embed.description += f"```\n{tb}```"
    embed.set_footer(text=f"{ctx.bot.user.name} Logging", icon_url=ctx.me.avatar_url_as(static_format="png"))
    embed.timestamp = datetime.datetime.utcnow()
    await ctx.bot.log_channel.send(embed=embed)

async def guild_joiner(guild):
    await ctx.bot.log_channel.send(guild.name+" joined")

async def guild_leaver(guild):
     ctx.bot.log_channel.send(guild.name+" leaved")

def setup(bot):
    bot.add_listener(error_manager,'on_command_error')
    bot.add_listener(guild_joiner,'on_guild_join')
    bot.add_listener(guild_leaver,'on_guild_remove')
