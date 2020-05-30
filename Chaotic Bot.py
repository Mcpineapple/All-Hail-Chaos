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

        self.first_on_ready = True

        self.load_extension('data.data')

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
            success = 0
            for ext in self.extensions_list:
                    if not ext in self.extensions:
                        try:
                            self.load_extension(ext)
                            report.append(f"✅ | **Extension loaded** : `{ext}`")
                            success+=1
                        except commands.ExtensionFailed as e:
                            report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
                        except commands.ExtensionNotFound:
                            report.append(f"❌ | **Extension not found** : `{ext}`")
                        except commands.NoEntryPointError:
                            report.append(f"❌ | **setup not defined** : `{ext}`")

            embed = Embed(title = f"{success} extensions were loaded & {len(self.extensions_list) - success} extensions were not loaded", description = '\n'.join(report), color = self.colors['green'])
            await self.log_channel.send(embed = embed)
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self,guild):
        await self.log_channel.send(guild.name+" joined")

    async def on_guild_remove(self,guild):
         await self.log_channel.send(guild.name+" left")

    async def close(self):
        await self.aio_session.close()
        await self.db.close()
        await self.ksoft_client.close()
        for task in all_tasks(loop = self.loop):
            task.cancel()
        await super().close()

    async def cog_reloader(self, ctx, extensions):
        self.last_update = datetime.utcnow()
        report = []
        success = 0
        self.reload_extension('data.data')
        M = len(self.extensions_list)
        if extensions:
            M = len(extensions)
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            success+=1
                            report.append(f"✅ | **Extension reloaded** : `{ext}`")
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            success+=1
                            report.append(f"✅ | **Extension loaded** : `{ext}`")
                    except commands.ExtensionFailed as e:
                        report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
                    except commands.ExtensionNotFound:
                        report.append(f"❌ | **Extension not found** : `{ext}`")
                    except commands.NoEntryPointError:
                        report.append(f"❌ | **setup not defined** : `{ext}`")
                else:
                    report.append(f"❌ | `{ext}` is not a valid extension")
        else:
            for ext in self.extensions_list:
                try:
                    try:
                        self.reload_extension(ext)
                        success+=1
                        report.append(f"✔️ | **Extension reloaded** : `{ext}`")
                    except commands.ExtensionNotLoaded:
                        self.load_extension(ext)
                        report.append(f"✔️ | **Extension loaded** : `{ext}`")
                except commands.ExtensionFailed as e:
                    report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
                except commands.ExtensionNotFound:
                    report.append(f"❌ | **Extension not found** : `{ext}`")
                except commands.NoEntryPointError:
                    report.append(f"❌ | **setup not defined** : `{ext}`")

        embed = Embed(title = f"{success} {'extension was' if success == 1 else 'extensions were'} loaded & {M - success} {'extension was' if M - success == 1 else 'extensions were'} not loaded", description = '\n'.join(report), color = self.colors['green'])
        await self.log_channel.send(embed = embed)
        await ctx.send(embed = embed)

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
