#=================IMPORT==============#
import discord # py -m pip install discord
import discord.types
from discord.ext import commands
from discord import TextChannel, Client, Embed, Member, Message, user, Interaction, PartialMessage

import traceback
import re
import asyncio
import time
from datetime import datetime, timezone

from bot_IO import Save, Load
from util import listState, Channels, urlState, Roles, Data, secret, savefile
#=================IMPORT==============#



#=================INITIALIZATION==============#
global intents
intents = discord.Intents.all()

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        global intents
        intents = intents.all()
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents, *args, **kwargs)

        self.variable = 0
    
    async def setup_hook(self) -> None:
        print(f"SETUP HOOK")

        # For dynamic items, we must register the classes instead of the views.
        self.guild = bot.get_guild(int(secret.guild))

bot = Bot()
#=================INITIALIZATION==============#



# ACTUALLY EVENT CALLBACK METHODS

@bot.event
async def on_ready():
    try:await Ready()
    except:traceback.print_exc()

@bot.event
async def on_message(message:Message):
    try:await MessageSent(message=message)
    except:traceback.print_exc()

@bot.event
async def on_member_remove(member:Member): await Left(member)

@bot.event
async def on_member_join(member:Member): await Join(member)

@bot.event
async def on_raw_reaction_add(ctx:discord.RawReactionActionEvent): await ReactionAdded(ctx)

@bot.event
async def on_message_delete(message:Message): 
    print(f"message deleted [{message.content}]") # prints to console
    pass # does nothing

# ACTUALLY EVENT CALLBACK METHODS



# EVENT-BASED METHODS

async def Ready():

    bot.u = {}

    bot.u[Data.urllist] = await Load(savefile.urls)

    print(f"\n\n[Welcome] Connected!")
    print(f"[Welcome] Name:\t\t\t\t\t\t\t {bot.user.name}")
    print(f"[Welcome] ID:\t\t\t\t\t\t\t {bot.user.id}")
    print(f"[Welcome] GUILD:\t\t\t\t\t\t\t {secret.guild.name}\n\n")

    try:await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name='Smol Adventure',
            )
            )
    except: traceback.print_exc()

    try: guild = bot.get_guild(int(secret.guild))
    except: traceback.print_exc()

    return

async def MessageSent(message:Message):

    try: await bot.process_commands(message)
    except Exception as e: traceback.print_exc()

    global exceptList


    #BOTS
    # quit this method ('MessageSent') if it's a bot talking (example this bot + avoids infinite loop)
    if message.author.bot == True: return 

    #DIRECT MESSAGE
    elif isinstance(message.channel, discord.channel.DMChannel):
        try: await DM(message=message)
        except Exception as e: traceback.print_exc()
        return

    #WELCOME CHANNEL
    # I would only like to allow 'Waving' in the welcome channel so:
    # here, we don't allow chat in welcome channel (I do this here instead of in discord because 'send message' channel perms are needed for waving)
    elif(message.channel.id == Channels.welcome and (message.content.__len__() > 0 or message.components.__len__() > 0)):
        
        # we DM the user their message so that they don't have to rewrite it (kindness matters)
        try:await message.author.send(f"Please repost in the appropriate channels. #Welcome is not a conversation channel.\n```{message.content}```")
        except:traceback.print_exc()

        # delete their message
        await message.delete()

        # quit this method ('MessageSent')
        return

    #REGULAR
    else:
        try:
            #intro role removal
            try:
                if(message.channel.id == Channels.introductions and message.author.get_role(Roles.intro) is not None):
                    guild = bot.get_guild(int(secret.guild))
                    role = guild.get_role(Roles.intro)
                    await message.author.remove_roles(role)
            except Exception: traceback.print_exc()


            if(str(message.content).__contains__("@everyone") or str(message.content).__contains__("@here")):
                    
                    # allow @everyone for admins
                    if message.author.guild_permissions.administrator:
                        await message.channel.send(content="I'll allow it.", delete_after=10.0)

                    # not for anyone else
                    else: 
                        # we DM the user their message so that they don't have to rewrite it (kindness matters)
                        try:await message.author.send(f"```{message.content}```")
                        except:traceback.print_exc()
                        
                        # delete their message
                        await message.delete()
                        
                        # send public warning so we can tell the bot prevented it and for whom
                        await message.channel.send(content=f"{message.author.display_name}, the use of `@everyone` and `@here` are not allowed in this server.")


            #URL

            # scan message for urls
            try: urls = FindUrls(message.content)
            except: traceback.print_exc()
            
            # url(s) detected
            if (len(urls) > 0):
                # allow any url for admins
                if(message.author.guild_permissions.administrator): return

                # it's difficult to detect multiple urls and separate them so we only allow one
                if (len(urls) > 1):


                    # we DM the user their message so that they don't have to rewrite it (kindness matters)
                    try:await message.author.send(f"```{message.content}```")
                    except:traceback.print_exc()

                    await message.channel.send("Only one url is allowed per message!", delete_after=30.0)
                    
                    # delete their message
                    await message.delete()

                else: # only 1 url

                    # note: message deletion happens inside the CheckUrl and CheckDomain as soon as one of them fails (finds that a url is blocked by you).

                    # first we check if this SPECIFIC url has been allowed
                    # example: perhaps we would like to block all gofund.me urls but not gofund.me/my_personal_fundraiser
                    URLSuccess = await CheckUrl(message=message, urls=urls)

                    # if the full url is not allowed, then check if the domain in general is allowed
                    # example: 
                    # Netflix has no user submited content and therefore should always be safe, 
                    # so:
                    # netflix.*anything*/*anything*
                    # can be allowed
                    if(URLSuccess == False): await CheckDomain(message=message, urls=urls)

        except: traceback.print_exc()

async def DM(message: Message):

    text = message.content

    print(f"{text}")

async def Left(member:Member):
    await asyncio.sleep(5)
    print(f"member left:\t\t\t\t\t\t\t {member.display_name}")

async def Join(member:Member):

    now = datetime.now().replace(tzinfo=timezone.utc)
    created =   member.created_at.replace(tzinfo=timezone.utc)
    uCreated = time.mktime(created.timetuple()).__round__()

    print(f"created: {uCreated}")

    await asyncio.sleep(5)

    uNow = time.mktime(now.timetuple())
    epochMonth = 2629743 
    epochYear = 31556926

    print(f"created delta: {uNow - uCreated}")
    
    if(abs(uNow - uCreated) < epochYear):return
    else:
        guild = bot.get_guild(int(secret.guild))
        access = guild.get_role(Roles.access)
        await member.add_roles(access)

    print(f"{member.display_name} joined!")

async def ReactionAdded(ctx:discord.RawReactionActionEvent):
    try:
        if(ctx.member.bot): return print("is bot")
        if(ctx.emoji.name == "🦺"): pass
    except Exception: traceback.print_exc()

# EVENT-BASED METHODS



# URL-BASED METHODS

async def AddUrl(url: str, state: int):

    try:
        print(f"newentry {url} {listState(state).name}")
        bot.u[Data.urllist][url] = {}
        bot.u[Data.urllist][url]['state'] = state
    except: traceback.print_exc()

    await Save(data=bot.u[Data.urllist], name=savefile.urls)

async def CheckDomain(message:Message, urls: list[str]):

    try:
        try: domain = FindUrlDomain(message.content)
        except: traceback.print_exc()
        domain = domain.casefold().strip()
        print(f"domain: {domain}")

        #unknown domain
        if(bot.u[Data.urllist].keys().__contains__(domain) == False or bot.u[Data.urllist][domain]['state'] == urlState.unused):
            await message.channel.send(content="Only whitelisted domains are allowed in this server!", delete_after=30.0)
            try: print(f"domain state:\t\t\t\t\t\t\t {bot.u[Data.urllist][domain]['state']} | channel.id: {message.channel.id}")
            except: pass
            await message.delete()
            await AddUrl(url=domain,state=listState.unused) #add domain
            await Save(bot.u[Data.urllist], savefile.urls)
            print(f"url\t[{urlState.block.name}ed]")
            return

        #blocked domain
        if(bot.u[Data.urllist][domain]['state'] == urlState.block):
            print(f"domain state:\t\t\t\t\t\t\t {bot.u[Data.urllist][domain]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Url domain contained content that has been blacklist by the server", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return

        #fund domain in other channel
        if(bot.u[Data.urllist][domain]['state'] == urlState.fundraising and message.channel.id != Channels.fundraisers):
            print(f"domain state:\t\t\t\t\t\t\t {bot.u[Data.urllist][domain]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Fundraising domains are not allowed in this channel!", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return

        #other domain in fund channel
        if(bot.u[Data.urllist][domain]['state'] != urlState.fundraising and message.channel.id == Channels.fundraisers):
            print(f"domain state:\t\t\t\t\t\t\t {bot.u[Data.urllist][domain]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Only whitelisted funding domains are allowed in this channel!", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return

    except:
        await message.delete()
        print(f"url\t[{urlState.block.name}ed]")
        traceback.print_exc()

async def CheckUrl(message:Message, urls: list[str]):

    URLSuccess = True

    try:
        try: url = urls[0].casefold().strip()
        except: traceback.print_exc()

        print(f"urls[0]:\t{url}\tfrom:\t{message.author.display_name}\tin:\t{message.channel.name}")

        #allowed url in any channel
        if(bot.u[Data.urllist].keys().__contains__(url) == True and bot.u[Data.urllist][url]['state'] == urlState.allow):
            URLSuccess = True
            print(f"url\t[{urlState.allow.name}ed]")
            return URLSuccess

        #blocked url
        if(bot.u[Data.urllist].keys().__contains__(url) == True and bot.u[Data.urllist][url]['state'] == urlState.block):
            print(f"url state:\t\t\t\t\t\t\t {bot.u[Data.urllist][url]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Url contained content that has been blacklist by the server", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return URLSuccess

        #fund url in other channel
        if(bot.u[Data.urllist].keys().__contains__(url) == True and bot.u[Data.urllist][url]['state'] == urlState.fundraising and message.channel.id != Channels.fundraisers):
            print(f"url state:\t\t\t\t\t\t\t {bot.u[Data.urllist][url]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Fundraising links are not allowed in this channel!", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return URLSuccess

        #other url in fund channel
        if(bot.u[Data.urllist].keys().__contains__(url) == True and bot.u[Data.urllist][url]['state'] != urlState.fundraising and message.channel.id == Channels.fundraisers):
            print(f"url state:\t\t\t\t\t\t\t {bot.u[Data.urllist][url]['state']} | channel.id: {message.channel.id}")
            await message.channel.send(content="Only whitelisted funding urls are allowed in this channel!", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            return URLSuccess

        #fund url in fund channel
        if(bot.u[Data.urllist].keys().__contains__(url) == True and bot.u[Data.urllist][url]['state'] == urlState.fundraising and message.channel.id == Channels.fundraisers):
            URLSuccess = True
            print(f"url\t[{urlState.allow.name}ed]")
            return URLSuccess

        #unknown url
        if(bot.u[Data.urllist].keys().__contains__(url) == False or bot.u[Data.urllist][url]['state'] == urlState.unused):
            try:
                try: domain = FindUrlDomain(message.content)
                except: traceback.print_exc()
                domain = domain.casefold().strip()
                print(f"domain 0: {domain}")

                #allowed domain in any channel
                if(
                    (bot.u[Data.urllist][domain]['state'] == urlState.allow and message.channel.id != Channels.fundraisers)
                    or
                    (bot.u[Data.urllist][domain]['state'] == urlState.fundraising and message.channel.id == Channels.fundraisers)
                    ):
                    URLSuccess = True
                    print(f"url\t[{urlState.allow.name}ed]")
                    return URLSuccess

                #unknown domain
                if(bot.u[Data.urllist].keys().__contains__(domain) == False or bot.u[Data.urllist][domain]['state'] == 0):
                    await AddUrl(url=domain,state=listState.unused) #add domain
                    await Save(bot.u[Data.urllist], savefile.urls)
            except:traceback.print_exc()

            try: print(f"url state:\t\t\t\t\t\t\t {bot.u[Data.urllist][url]['state']} | channel.id: {message.channel.id}")
            except: pass
            await message.channel.send(content="Only whitelisted urls are allowed in this server!", delete_after=30.0)
            await message.delete()
            print(f"url\t[{urlState.block.name}ed]")
            await AddUrl(url=url,state=listState.unused) #add url
            await Save(bot.u[Data.urllist], savefile.urls)
            return URLSuccess

        print(f"url state:\t\t\t\t\t\t\t {bot.u[Data.urllist][url]['state']}")
        URLSuccess = False

    except:
        traceback.print_exc()
        URLSuccess = False

    return URLSuccess

# URL-BASED METHODS



# UTILITY METHODS


def FindUrls(string:str):
    # finds all the urls in a message
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)

    return [x[0] for x in url]

def FindUrlDomain(string:str):
    # finds the domain address of the url
    regex = r"(?i)\b(?:https?://|www\d{0,3}[.]|([a-z0-9.\-]+)[.][a-z]{2,4}/)"
    url = re.findall(regex, string)
    print(f"url:\t\t\t\t\t\t\t {url}")
    for x in url:
        if(x is not None and len(x) > 0):
            print(f"result:\t\t\t\t\t\t\t {x}")
            return x

# UTILITY METHODS



# BOOTING UP THE PROGRAM

async def main():

    async with bot:
        bot.remove_command('help')

        await bot.start(secret.token)

asyncio.run(main())

# BOOTING UP THE PROGRAM