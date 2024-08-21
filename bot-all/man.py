
import discord
from decouple import config
from discord.ext import commands
from move_users import move_users
from strava_activities import strava_activities
from strava_table import strava_table
from utils import msg_time

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', 0))

INTENTS = discord.Intents.default()
BOT = commands.Bot(command_prefix='?', intents=INTENTS)


@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}')
    move_users.start(BOT, GUILD_ID)
    strava_activities.start(BOT)
    strava_table.start(BOT, GUILD_ID)


if __name__ == '__main__':
    try:
        BOT.run(TOKEN)
    except Exception as e:
        print(f'{msg_time()} {e}')
