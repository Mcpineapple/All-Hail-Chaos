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

from inspect import Parameter
from typing import Optional

import discord
from discord.ext import commands
import discord.utils

class Help(commands.HelpCommand):
    async def get_command_signature(self, command):
        basis = f"{command.name}"
        for arg in command.clean_params.values():
            if arg.default == Parameter.empty and arg.annotation not in [Optional, commands.Greedy] and arg.kind not in [Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL]:
                basis+=f" <{arg.name}>"
            else:
                basis+=f" [{arg.name}]"
        return basis

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title = "List of all the commands", description = f'Command syntax : `<Those arguments are required>`. `[Those aren\'t]`\n[Everything to know about my glorious self]({discord.utils.oauth_url(str(ctx.bot.user.id), permissions = discord.Permissions(ctx.bot.invite_permissions))} "Invite link")\nThe prefix for this channel is `{discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}`', colour = ctx.bot.colors['blue'])
        embed.set_author(name = str(ctx.message.author), icon_url = str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
        embed.set_footer(text = f"To get more information, use {discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}help [subject].", icon_url = str(ctx.bot.user.avatar_url))
        for cog in mapping:
            command_list = [f"`{discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}{await self.get_command_signature(command)}` : {command.short_doc}" for command in await self.filter_commands(mapping[cog])]
            if command_list:
                if cog:
                    embed.add_field(name = cog.qualified_name, value = '\n'.join(command_list), inline=False)
                else:
                    embed.add_field(name = 'Other commands', value = '\n'.join(command_list))
        await ctx.send(embed = embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = discord.Embed(title = cog.qualified_name, description = f"Command syntax : `<Those arguments are required>`. `[Those aren't]`\nThe prefix for this channel is `{discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}`\n{cog.description}", colour = ctx.bot.colors['blue'])
        embed.set_author(name = str(ctx.message.author), icon_url = str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
        for command in await self.filter_commands(cog.get_commands()):
            embed.add_field(name = f"{discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}{await self.get_command_signature(command)}", value = command.help, inline=False)
        embed.set_footer(text = f"Are you interested in {command.name} ?", icon_url = str(ctx.bot.user.avatar_url))
        await ctx.send(embed = embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(title = f"{discord.utils.escape_markdown(await ctx.bot.get_m_prefix(ctx.message, False))}{await self.get_command_signature(command)}", description = f"Command syntax : `<Those arguments are required>`. `[Those aren't]`\n{command.help}", colour = ctx.bot.colors['blue'])
        if command.aliases:
            embed.add_field(name = "Aliases :", value = "\n".join(command.aliases))
        embed.set_author(name = str(ctx.message.author), icon_url = str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
        if command.hidden:
            embed.set_footer(text = f"Wow, you found {command.name} !", icon_url = str(ctx.bot.user.avatar_url))
        else:
            embed.set_footer(text = f"Are you interested in {command.name} ?", icon_url = str(ctx.bot.user.avatar_url))
        await ctx.send(embed = embed)

    async def send_error_message(self, error):
        ctx = self.context
        await ctx.bot.httpcat(ctx, 404, error)

def setup(bot):
    bot.old_help_command = bot.help_command
    bot.help_command = Help(verify_checks = False, command_attrs = {'hidden':True})

def teardown(bot):
    bot.help_command = bot.old_help_command