
from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import commands, tasks

TOKEN = config('TOKEN_STRAVA_TABLE', '')  # noqa: E501
GUILD_ID = config('GUILD_ID_STRAVA_TABLE', '')

CHANNEL_ID = config('CHANNEL_ID_STRAVA_TABLE', '')

LOOP_INTERVAL_STRAVA_TABLE = int(config('LOOP_INTERVAL_STRAVA_TABLE', 1))

URL_GROUP = config('URL_GROUP_STRAVA_TABLE', '')  # noqa: E501
URL_TABLE = config('URL_TRABLE_STRAVA_TABLE', '')  # noqa: E501
URL_GROUP_INFO = config('URL_GROUP_INFO_STRAVA_TABLE', '')  # noqa: E501


def scrape_strava_activities():
    response_table = requests.get(URL_TABLE)
    soup_table = BeautifulSoup(response_table.text, 'html.parser')

    response_info = requests.get(URL_GROUP_INFO)
    soup_info = BeautifulSoup(response_info.text, 'html.parser')

    runs = soup_info.select_one('.list-stats > li:nth-child(1) > div:nth-child(1) > b:nth-child(2)').text.strip()  # noqa: E501
    distance = soup_info.select_one('.list-stats > li:nth-child(2) > div:nth-child(1) > b:nth-child(2)').text.strip()  # noqa: E501
    time = soup_info.select_one('.list-stats > li:nth-child(3) > div:nth-child(1) > b:nth-child(2)').text.strip()  # noqa: E501
    elevation = soup_info.select_one('.list-stats > li:nth-child(4) > div:nth-child(1) > b:nth-child(2)').text.strip()  # noqa: E501

    activities = []

    group_title = soup_table.select_one('.secondary').text.strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    activities.append(
        f'# [{group_title}]({URL_GROUP}) - Latest Runs [{date}]\n'
    )

    activities.append(
        f'## Informações do Grupo:\n Runs: **{runs}** | Distance: **{distance}** | Time: **{time}** | Elevation: **{elevation}**\n'  # noqa: 501
    )

    for li in soup_table.select('ul.activities > li'):
        athlete_name = li.select_one('.athlete-name').text.strip()
        activity_name = li.select_one('h3 strong a').text.strip()
        stats = [stat.text for stat in li.select('ul.stats li')]
        distance, time, elevation = stats[0], stats[1], stats[2]
        timestamp = li.select_one('.timestamp').text.strip()

        activities.append(f"**{athlete_name}** - {activity_name}\n{distance}, {time}, {elevation}\n*{timestamp}*\n")   # noqa: E501

    return activities


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    send_strava_activities.start()


@tasks.loop(minutes=LOOP_INTERVAL_STRAVA_TABLE)
async def send_strava_activities():
    guild = bot.get_guild(int(GUILD_ID))
    channel = guild.get_channel(int(CHANNEL_ID))
    activities = scrape_strava_activities()

    if activities:
        await channel.send("\n".join(activities))
    else:
        await channel.send("No activities found.")


bot.run(TOKEN)
