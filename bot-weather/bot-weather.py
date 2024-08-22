from datetime import datetime

import discord
import requests
from decouple import config
from discord.ext import commands, tasks

TOKEN = config('TOKEN', '')
GUILD_ID = int(config('GUILD_ID', ''))

INTENTS = discord.Intents.default()
BOT = commands.Bot(command_prefix='?', intents=INTENTS)


CHANNEL_ID = int(config('CHANNEL_ID', ''))

GNEWS_BASE_URL = config('GNEWS_BASE_URL', '')

params = {
    "apiKey": config('GNEWS_API_KEY', ''),
    "sortBy": "publishedAt",
    "language": "pt",
    "from": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
}


@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}')
    weather.start()


@tasks.loop(minutes=1)
async def weather():
    GUILD = BOT.get_guild(GUILD_ID)
    channel = GUILD.get_channel(CHANNEL_ID)

    print(params['from'])

    # response = requests.get(WEATHER_BASE_URL, params=params)
    # await channel.send(response.json())
    #
    # embed = discord.Embed(
    #     title="📢 Anúncio Importante",
    #     description="Aqui está uma mensagem mais bonita e organizada usando **embeds**!",
    #     color=discord.Color.blue()
    # )
    #
    # embed.add_field(
    #     name="🌟 Destaque",
    #     value="Você pode adicionar campos com diferentes informações.",
    #     inline=False
    # )
    #
    # embed.add_field(
    #     name="📅 Data",
    #     value=["22 de agosto de 2024", response.json()['weather']],
    #     inline=True
    # )
    #
    # embed.set_footer(text="Mensagem enviada pelo bot")
    # embed.set_thumbnail(url="https://exemplo.com/imagem.png")
    #
    # await channel.send(embed=embed)
    #

BOT.run(TOKEN)
