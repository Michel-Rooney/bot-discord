from datetime import datetime

import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import tasks

STRAVA_TABLE_CHANNEL_ID = int(config('CHANNEL_ID_STRAVA_TABLE', 0))

STRAVA_TABLE_LOOP_INTERVAL_MIN = int(config('LOOP_INTERVAL_STRAVA_TABLE', 2))

STRAVA_TABLE_URL_GROUP = config('URL_GROUP_STRAVA_TABLE', '')
STRAVA_TABLE_URL_TABLE = config('URL_TRABLE_STRAVA_TABLE', '')
STRAVA_TABLE_URL_GROUP_INFO = config('URL_GROUP_INFO_STRAVA_TABLE', '')

RUNS_CSS = '.list-stats > li:nth-child(1) > div:nth-child(1) > b:nth-child(2)'
TIME_CSS = '.list-stats > li:nth-child(3) > div:nth-child(1) > b:nth-child(2)'
DISTANCE_CSS = (
    '.list-stats > li:nth-child(2) >'
    'div:nth-child(1) > b:nth-child(2)'
)
ELEVATION_CSS = (
    '.list-stats > li:nth-child(4) >'
    'div:nth-child(1) > b:nth-child(2)'
)


def scrape_strava_table():
    response_table = requests.get(STRAVA_TABLE_URL_TABLE)
    soup_table = BeautifulSoup(response_table.text, 'html.parser')

    response_info = requests.get(STRAVA_TABLE_URL_GROUP_INFO)
    soup_info = BeautifulSoup(response_info.text, 'html.parser')

    runs = soup_info.select_one(RUNS_CSS).text.strip()
    distance = soup_info.select_one(DISTANCE_CSS).text.strip()
    time = soup_info.select_one(TIME_CSS).text.strip()
    elevation = soup_info.select_one(ELEVATION_CSS).text.strip()

    activities = []

    group_title = soup_table.select_one('.secondary').text.strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    activities.append(
        f'# [{group_title}]({STRAVA_TABLE_URL_GROUP}) - Latest Runs [{date}]\n'
    )

    activities.append(
        '## Informações do Grupo:\n'
        f'Runs: **{runs}** | Distance: **{distance}** |'
        'Time: **{time}** | Elevation: **{elevation}**\n'
    )

    for li in soup_table.select('ul.activities > li'):
        athlete_name = li.select_one('.athlete-name').text.strip()
        activity_name = li.select_one('h3 strong a').text.strip()
        stats = [stat.text for stat in li.select('ul.stats li')]
        distance, time, elevation = stats[0], stats[1], stats[2]
        timestamp = li.select_one('.timestamp').text.strip()

        activities.append(
            f'**{athlete_name}** - {activity_name}\n',
            f'{distance}, {time}, {elevation}\n*{timestamp}*\n'
        )

    return activities


@tasks.loop(minutes=STRAVA_TABLE_LOOP_INTERVAL_MIN)
async def strava_table(BOT, GUILD_ID):
    guild = BOT.get_guild(GUILD_ID)
    channel = guild.get_channel(STRAVA_TABLE_CHANNEL_ID)
    activities = scrape_strava_table()

    if activities:
        await channel.send("\n".join(activities))
    else:
        await channel.send("No activities found.")
