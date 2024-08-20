import json
import os
from datetime import datetime

import discord
import requests
from decouple import config
from discord.ext import commands, tasks

# TOKEN DO BOT
TOKEN = config('TOKEN_STRAVA', '')
GUILD_ID = config('GUILD_ID_STRAVA', '')  # ID DO SERVER

CHANNEL_ID = config('CHANNEL_ID_STRAVA', '')  # CHAT-GERAL

# TEMPO DO LOOP DA VERIFICAÇÃO
LOOP_INTERVAL = int(config('LOOP_INTERVAL_STRAVA', 2))

BEARER_TOKEN = config('BEARER_TOKEN_STRAVA', '')
URL = config('URL_STRAVA', '')
FILENAME = config('FILENAME_STRAVA', '')

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    request_strava_activities.start()


@tasks.loop(minutes=LOOP_INTERVAL)
async def request_strava_activities():
    response = requests.get(URL, headers=headers)
    response_data = response.json()
    json_cache = None

    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) > 0:
        with open(FILENAME, 'r') as json_file:
            try:
                json_cache = json.load(json_file)
            except json.JSONDecodeError:
                print(
                    f"[{datetime.now()}]",
                    "Erro ao decodificar o arquivo JSON existente."
                )

    if json_cache != response_data:
        with open(FILENAME, 'w') as json_file:
            json.dump(response_data, json_file, indent=4)

        channel = bot.get_channel(int(CHANNEL_ID))
        if channel is not None:
            for activity in response_data:
                athlete = activity.get('athlete', {})
                firstname = athlete.get('firstname', 'N/A')
                lastname = athlete.get('lastname', 'N/A')
                name = activity.get('name', 'N/A')
                distance = activity.get('distance', 'N/A')
                moving_time = activity.get('moving_time', 'N/A')
                elapsed_time = activity.get('elapsed_time', 'N/A')
                elevation_gain = activity.get('total_elevation_gain', 'N/A')
                activity_type = activity.get('type', 'N/A')
                sport_type = activity.get('sport_type', 'N/A')
                workout_type = activity.get('workout_type', 'N/A')

                message = (
                    "========================================"
                    f"Athlete: {firstname} {lastname}\n"
                    f"Activity Name: {name}\n"
                    f"Distance: {distance} meters\n"
                    f"Moving Time: {moving_time} seconds\n"
                    f"Elapsed Time: {elapsed_time} seconds\n"
                    f"Total Elevation Gain: {elevation_gain} meters\n"
                    f"Type: {activity_type}\n"
                    f"Sport Type: {sport_type}\n"
                    f"Workout Type: {workout_type}\n"
                    "========================================"
                )

                await channel.send(message)
                print(f'[{datetime.now()}] {message}')
        else:
            print(f"[{datetime.now()}] Channel not found!")
    else:
        print(f'[{datetime.now()}] Informação igual')

bot.run(TOKEN)
