import json
import os

import requests
from decouple import config
from discord.ext import tasks
from utils import msg_time

STRAVA_ACT_BEARER_TOKEN = config('STRAVA_ACT_BEARER_TOKEN', '')
STRAVA_ACT_URL = config('STRAVA_ACT_URL', '')
STRAVA_ACT_FILENAME = config('STRAVA_ACT_FILENAME', 'cache.json')
STRAVA_ACT_CHANNEL_ID = int(config('STRAVA_ACT_CHANNEL_ID', 0))
STRAVA_ACT_LOOP_INTERVAL_MIN = int(config('STRAVA_ACT_LOOP_INTERVAL_MIN', 2))


HEADERS = {
    "Authorization": f"Bearer {STRAVA_ACT_BEARER_TOKEN}"
}


@tasks.loop(minutes=STRAVA_ACT_LOOP_INTERVAL_MIN)
async def strava_activities(BOT):
    response = requests.get(STRAVA_ACT_URL, headers=HEADERS)
    response_data = response.json()
    json_cache = None

    if os.path.exists(STRAVA_ACT_FILENAME) and os.path.getsize(STRAVA_ACT_FILENAME) > 0:  # noqa: E501
        with open(STRAVA_ACT_FILENAME, 'r') as json_file:
            try:
                json_cache = json.load(json_file)
            except json.JSONDecodeError:
                print(
                    f'{msg_time()} STRAVA_ACT: ERRO AO DECODIFICAR',
                    'O ARQUIVO JSON EXISTENTE.'
                )

                return

    # if json_cache == response_data:
    #     print(f'{msg_time()} STRAVA_ACT: OS ARQUIVOS SÃO IGUAIS.')
    #     return

    # with open(STRAVA_ACT_FILENAME, 'w') as json_file:
    #     try:
    #         json.dump(response_data, json_file, indent=4)
    #     except json.JSONDecodeError:
    #         print(
    #             f'{msg_time()} STRAVA_ACT: ERRO AO DECODIFICAR',
    #             'O ARQUIVO JSON EXISTENTE.'
    #         )
    #         return

    channel = BOT.get_channel(STRAVA_ACT_CHANNEL_ID)

    if channel is None:
        print(f'{msg_time()} STRAVA_ACT: CANAL NÃO ENCONTRADO.')
        return

    for activity in json_cache:
        athlete = activity.get('athlete', {})
        distance = activity.get('distance', 'N/A')
        moving_time = activity.get('moving_time', 'N/A')
        elapsed_time = activity.get('elapsed_time', 'N/A')

        if isinstance(distance, int) and distance > 0:
            distance = round((distance / 1000), 2)

        if isinstance(moving_time, int) and moving_time > 0:
            moving_time = round((moving_time / 60), 2)

        message = (
            f'[CLUBE DA CORRIDA] **{athlete}** acabou de correr'
            f'**{distance}** Km, no tempo de **{moving_time}**'
            f'o pace médio foi de **{elapsed_time}**.'
        )

        await channel.send(message)
        print(f'{msg_time()} {message}')
