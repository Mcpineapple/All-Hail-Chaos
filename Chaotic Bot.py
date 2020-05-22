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
from discord import Embed, Game
from datetime import datetime

import aiosqlite

from asyncio import all_tasks
import aiohttp

from os import path

import dbl
from github import Github

class chaotic_bot(commands.Bot):
    """The subclassed bot class"""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.load_extension('data.data')

        self.first_on_ready = True

        if self.dbl_token:
            self.dbl_client = dbl.DBLClient(self, self.dbl_token, autopost=True)

        if self.github_token:
            self.github = Github(self.github_token)

    async def on_ready(self):
        await self.change_presence(activity=Game(self.default_prefix+'help'))
        if self.first_on_ready:
            self.first_on_ready = False
            self.db = await aiosqlite.connect('data'+path.sep+'database.db')
            self.db.row_factory = aiosqlite.Row
            await self.db.execute("CREATE TABLE IF NOT EXISTS swear (id INT PRIMARY KEY NOT NULL, manual_on BOOL DEFAULT 0, autoswear BOOL DEFAULT 0, notification BOOL DEFAULT 1)")
            await self.db.execute('CREATE TABLE IF NOT EXISTS roles (message_id INT, channel_id INT, guild_id INT, emoji TINYTEXT, roleids TEXT)')
            self.aio_session = aiohttp.ClientSession()
            self.last_update = datetime.utcnow()
            self.log_channel = self.get_channel(self.log_channel_id)
            self.suggestion_channel = self.get_channel(self.suggestion_channel_id)
            report = []
            for ext in self.extensions_list:
                    if not ext in self.extensions:
                        try:
                            self.load_extension(ext)
                            report.append("Extension loaded : "+ext)
                        except commands.ExtensionFailed as e:
                            report.append(e.name+" : " + str(type(e.original)) + " : " + str(e.original))
                        except:
                            report.append("Extension not loaded : "+ext)
            await self.log_channel.send('\n'.join(report))
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self,guild):
        await self.log_channel.send(guild.name+" joined")

    async def on_guild_remove(self,guild):
         await self.log_channel.send(guild.name+" leaved")

    async def close(self):
        await self.aio_session.close()
        await self.db.close()
        if hasattr(self,"session"):
            await self.session.close()
        for task in all_tasks(loop=self.loop):
            task.cancel()
        await super().close()

    async def cog_reloader(self, extensions):
        self.last_update=datetime.utcnow()
        report=[]
        self.reload_extension('data.data')
        if extensions:
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            report.append("Extension reloaded : "+ext)
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            report.append("Extension loaded : "+ext)
                    except commands.ExtensionFailed as e:
                        report.append(e.name+" : "+str(type(e.original))+" : "+str(e.original))
                    except:
                        report.append("Extension not loaded : "+ext)
                else:
                    report.append(f"`{ext}` is not a valid extension")
        else:
            for ext in self.extensions_list:
                try:
                    try:
                        self.reload_extension(ext)
                        report.append("Extension reloaded : "+ext)
                    except commands.ExtensionNotLoaded:
                        self.load_extension(ext)
                        report.append("Extension loaded : "+ext)
                except commands.ExtensionFailed as e:
                    report.append(e.name+" : "+str(type(e.original))+" : "+str(e.original))
                except:
                    report.append("Extension not loaded : "+ext)
        await self.log_channel.send('\n'.join(report))

    async def get_m_prefix(self, message, not_print=True):
        if message.content.startswith("¤") and not_print:
            return '¤'
        elif message.content.startswith(self.default_prefix+"help") and not_print:
            return self.default_prefix
        if not hasattr(self, 'db'):
            return self.default_prefix
        await self.db.execute('CREATE TABLE IF NOT EXISTS prefixes (ctx_id INT PRIMARY KEY, prefix TINYTEXT)')
        cur = await self.db.execute('SELECT * FROM prefixes WHERE ctx_id=?', (self.get_id(message),))
        result = await cur.fetchone()
        if result:
            return result['prefix']
        return self.default_prefix

    async def httpcat(self, ctx, code, title = Embed.Empty, description = Embed.Empty):
        embed = Embed(title = title, color = self.colors['red'], description = description)
        embed.set_image(url = "https://http.cat/"+str(code)+".jpg")
        await ctx.send(embed=embed)

    @staticmethod
    def get_id(ctx):
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

async def command_prefix(bot,message):
    return await bot.get_m_prefix(message)

bot = chaotic_bot(command_prefix = command_prefix, description = "A bot for fun", fetch_offline_members = True)
bot.run(bot.token)
