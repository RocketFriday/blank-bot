from __future__ import unicode_literals
import enum
import dotenv # py -m pip install python-dotenv
import os
import traceback

try:
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if(os.path.exists(dotenv_path)): dotenv.load_dotenv(dotenv_path)
    else: input(f"Error: path does not exist: {dotenv_path}")
except Exception: traceback.print_exc()

class secret(enum.StrEnum):
    token           =os.environ.get("DISCORD_TOKEN")
    guild           =os.environ.get("DISCORD_GUILD")

class savefile(enum.StrEnum):
    urls = "urls"

class listState(enum.IntEnum):
    unused = 0
    allow = 1
    block = 2

class urlState(enum.IntEnum):
    unused = 0
    allow = 1
    block = 2
    fundraising = 3

class Roles(enum.IntEnum):
    intro = 1217995919962804295
    access = 940797478796685418

class Channels(enum.IntEnum):
    none               = 0
    generalChat          = 940797478922485763

# Bot data dictionary keys
class Data(enum.StrEnum):
    urllist = 'urls'
