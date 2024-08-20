import json
import os
from datetime import datetime

import discord
import requests
from discord.ext import commands, tasks

# TOKEN DO BOT
TOKEN = ''  # noqa: E501
GUILD_ID = ''  # ID DO SERVER


# MOVE USER
SOURCE_CHANNEL_ID = ''  # ORIGEM -> WEBCAM
TARGET_CHANNEL_ID = ''  # DESTINO -> GERAL
LOOP_INTERVAL_MOVE_USER = 2  # TEMPO DO LOOP DA VERIFICAÇÃO


# STRAVA
BEARER_TOKEN = ''
URL = ''  # noqa: E501
FILENAME = 'cache.json'
CHANNEL_ID_STRAVA = ''  # CHAT-GERAL
LOOP_INTERVAL_STRAVA = 2  # TEMPO DO LOOP DA VERIFICAÇÃO

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    move_users.start()
    request_strava_activities.start()


@tasks.loop(minutes=LOOP_INTERVAL_MOVE_USER)
async def move_users():
    guild = bot.get_guild(int(GUILD_ID))
    source_channel = guild.get_channel(int(SOURCE_CHANNEL_ID))
    target_channel = guild.get_channel(int(TARGET_CHANNEL_ID))

    if source_channel and target_channel:
        for member in source_channel.members:
            if not member.bot:
                if not member.voice.self_video and not member.voice.self_stream:  # noqa: E501
                    await member.move_to(target_channel)
                    try:
                        await member.send(f'**[MODERAÇÃO ESTUDOS EM EVIDÊNCIA]** Olá **{member.name}**, o canal **"(WEBCAM OU TELA ON)"** é apenas para câmeras ou streams ligadas. Portanto, você foi movido para sala **"GERAL"**.')  # noqa: 501
                        print(f'[{datetime.now()}] Moved {member.name} to {target_channel.name}')  # noqa: E501
                    except:
                        print(f'[{datetime.now()}] ERRO AO ENVIAR MENSAGEM: {member.name}')  # noqa: E501


@tasks.loop(minutes=LOOP_INTERVAL_STRAVA)
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

        channel = bot.get_channel(int(CHANNEL_ID_STRAVA))
        if channel is not None:
            for activity in response_data:
                athlete = activity.get('athlete', {})
                distance = activity.get('distance', 'N/A')
                moving_time = activity.get('moving_time', 'N/A')
                elapsed_time = activity.get('elapsed_time', 'N/A')

                if distance > 0:
                    distance = round((distance / 1000), 2)

                if moving_time > 0:
                    moving_time = round((moving_time / 60), 2)

                message = (
                    f'[CLUBE DA CORRIDA] **{athlete}** acabou de correr ',
                    f'**{distance}** Km, no tempo de **{moving_time}** ',
                    f'o pace médio foi de **{elapsed_time}**.'
                )

                await channel.send(message)
                print(f'[{datetime.now()}] {message}')
        else:
            print(f"[{datetime.now()}] Channel not found!")
    else:
        print(f'[{datetime.now()}] Informação igual')


bot.run(TOKEN)
