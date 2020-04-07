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

from discord.ext import commands
from discord import Embed,Game,Status
from data import data
import asyncio
import ksoftapi

import sqlite3

class chaotic_bot(commands.Bot):
    """The subclassed bot class"""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.lavalink_host=data.lavalink_host
        self.lavalink_port=data.lavalink_port
        self.lavalink_pw=data.lavalink_pw
        self.lavalink_region=data.lavalink_region

        self.http.user_agent=data.user_agent

        self.ksoft_token=data.ksoft_token

        self.db=sqlite3.connect("data/database.db")

        self.first_on_ready=True

    async def on_ready(self):
        if self.first_on_ready:
            self.log_channel=self.get_channel(data.log_channel)
            await bot.change_presence(activity=Game(self.get_first_prefix(bot.command_prefix)+'help'))
            report=[]
            for ext in data.extensions:
                    if not ext in bot.extensions:
                        try:
                            bot.load_extension(ext)
                            report.append("Extension loaded : "+ext)
                        except:
                            report.append("Extension not loaded : "+ext)
            await self.log_channel.send('\n'.join(report))
        else:
            await self.log_channel.send("on_ready called again")

    def get_first_prefix(self,obj):
            if type(obj)==str:
                return obj
            else:
                return obj[0]

    async def cog_reloader(self):
        report=[]
        for ext in data.extensions:
            if not "success" in ext:
                try:
                    self.reload_extension(ext)
                    report.append("Extension reloaded : "+ext)
                except:
                    report.append("Extension not reloaded : "+ext)
        await self.log_channel.send('\n'.join(report))


bot=chaotic_bot(command_prefix=('€','¤'),description="A bot for fun",help_command=None,fetch_offline_members=True)

@bot.command(hidden=True,ignore_extra=True)
async def help(ctx,*command_help):
    """Sends the help message
    Trust me, there's nothing to see here. Absolutely nothing."""
    if len(command_help)==0:
        #Aide générale
        embed=Embed(title='Help',description="Everything to know about my glorious self",colour=data.get_color())
        embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
        embed.set_footer(text=f"To get more information, use {get_first_prefix(bot.command_prefix)}help [subject].",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
        for cog in bot.cogs:
            if bot.get_cog(cog).get_commands():
                command_list=[get_first_prefix(bot.command_prefix)+command.name+' : '+command.short_doc for command in bot.get_cog(cog).get_commands() if not command.hidden]
                embed.add_field(name=bot.get_cog(cog).qualified_name,value='\n'.join(command_list),inline=False)
        command_list=[get_first_prefix(bot.command_prefix)+command.name+' : '+command.short_doc for command in bot.commands if not command.cog and not command.hidden]
        if command_list:
            embed.add_field(name='Other commands',value='\n'.join(command_list))
        await ctx.send(embed=embed)
    else:
        for helper in command_help:
            cog=bot.get_cog(helper)
            if cog:
                if cog.get_commands():
                    #Aide d'un cog
                    embed=Embed(title=helper,description=cog.description,colour=data.get_color())
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    for command in cog.get_commands():
                        if not command.hidden:
                            aliases=[command.name]
                            if command.aliases!=[]:
                                aliases+=command.aliases
                            embed.add_field(name='/'.join(aliases),value=command.help,inline=False)
                    embed.set_footer(text=f"Are you interested in {helper} ?",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    await ctx.send(embed=embed)
            else:
                cog=bot.get_command(helper)
                if cog:
                    #Aide d'une commande spécifique
                    embed=Embed(title=get_first_prefix(bot.command_prefix)+helper,description=cog.help,colour=data.get_color())
                    if cog.aliases!=[]:
                        embed.add_field(name="Aliases :",value="\n".join(cog.aliases))
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    if cog.hidden:
                        embed.set_footer(text=f"Wow, you found {helper} !",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    else:
                        embed.set_footer(text=f"Are you interested in {helper} ?",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"I couldn't find {helper}")

bot.client=ksoftapi.Client(bot.ksoft_token,bot,bot.loop)
bot.run(data.token)
