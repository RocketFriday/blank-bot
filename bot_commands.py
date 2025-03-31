from discord.ext import commands
from discord import app_commands
from discord import TextChannel
import discord


import asyncio
import traceback
from typing import List


from bot_IO import Save, Load
from util import urllistState, Channels, Data, secret, savefile




class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("commands module loaded")

    async def channel_autocomplete(self, ctx: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        choices: List[str] = [c.name for c in Channels]
        return [app_commands.Choice(name=ch, value=ch) for ch in choices if current.lower() in ch.lower()]

    async def urllist_autocomplete(self, ctx: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        choices: List[str] = [c if len(c) < 96 else f"...{c[len(c)-93:len(c)]}" for c in self.bot.u[Data.urllist].keys()]
        return [app_commands.Choice(name=ch, value=ch) for ch in choices if current.lower() in ch.lower()]


    @app_commands.command(name = "url", extras={'cat':'staff', 'prefix':'/'}, description= "allows or blocks urls in the server")
    @app_commands.autocomplete(url=urllist_autocomplete)
    async def urllist(self, ctx: discord.Interaction, state: urllistState,url: str = None):
        if(url is str):
            self.bot.u[Data.urllist][url.lower()] = int(state.value)
            await Save(data=self.bot.u[Data.urllist], name=savefile.urls)
            await ctx.response.send_message(f"urllist updated.", ephemeral=False)
        elif((url is None or url == "") and (id is None or id == 0) and state is not None):
            pass

    @app_commands.command(name='sync',  extras={'cat':'dev', 'prefix':'/'} , description='Updates and syncs all available bot commands with the server.')
    async def sync(self, ctx: discord.Interaction):
        print("sync command")

        if ctx.user.guild_permissions.administrator:
            # We'll copy in the global commands to test with:
            try:
                guild = discord.Object(ctx.guild.id)
                self.bot.tree.copy_global_to(guild=guild)
                # followed by syncing to the testing guild.
                # await bot.tree.sync() #resets a stuck sync

                cmdlist = await self.bot.tree.sync(guild=guild)

                s = ""
                for c in cmdlist: s += f"{c.name}\n"

                await ctx.response.send_message(f'Synced.\n{s}', ephemeral=True)
            except Exception as e: print(f'error:\t\t\t\t\t\t\t {e}')
            print(f"synced: {ctx.guild.name}")
        else: await ctx.response.send_message(content="'You must be an admin in order to use this command.'", ephemeral=True)

    @app_commands.command(name = "sendasbot", extras={'cat':'staff', 'prefix':'/'}, description= "send msgs as the bot.")
    @app_commands.autocomplete(channel=channel_autocomplete)
    async def sendasbot(self, ctx: discord.Interaction, channel: str, message:str):
        try:
            # if(message.author.guild_permissions.administrator or ctx.user.get_role(Roles.moderator) is not None):
            if(message.author.guild_permissions.administrator):
                for c in Channels:
                    if(channel == c.name):
                        message=message.replace('\\n', "\n").replace('\\t', "\t")
                        await SendAsBot(self=self, ctx=ctx, channelID=c.value, content=message)
                        print(f"{ctx.user.display_name} sent\n{message}\nin {c.name}\nas the bot.")
                        await ctx.response.send_message("done", delete_after=2.0, ephemeral=True)
                        return
                await ctx.response.send_message("could not find channel", delete_after=6.0, ephemeral=True)
            else: await ctx.response.send_message("you must be a member of the staff to you this cmd", delete_after=6.0, ephemeral=True)
        except Exception as e:
                print(e)
                if (ctx.response.is_done() == False): await ctx.response.send_message(f"error: {e}", delete_after=10.0, ephemeral=True)


async def AddUrl(self, url: str, state: int, ctx:commands.Context = None):
    self.bot.u[Data.urllist][url] = {}
    self.bot.u[Data.urllist][url]['state'] = state
    await Save(data=self.bot.u[Data.urllist], name=savefile.urls)

async def SendAsBot(self, ctx = None, channelID = None, content = None, reference = None, attachments = None, view = None):
    if(channelID is not None and content is not None):
        try:
            chan:TextChannel = await self.bot.fetch_channel(channelID)
            if(attachments is not None):
                files = []
                for a in attachments:
                    files.append(
                        await a.to_file()
                    )
                
                if(view): msg = await chan.send(content, reference=reference, files=files, view=view)
                else: msg = await chan.send(content, reference=reference, files=files)

            else:
                if(view): msg = await chan.send(content, reference=reference, view=view)
                else: msg = await chan.send(content, reference=reference)

            return msg
        except Exception: traceback.print_exc()
    pass

async def setup(bot): 
    await bot.add_cog(CommandsCog(bot), guilds=[discord.Object(id=secret.guild)])
