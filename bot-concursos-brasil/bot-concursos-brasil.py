from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from decouple import config
from discord.ext import commands, tasks

TOKEN = config('TOKEN', '')  # noqa: E501

INTENTS = discord.Intents.default()
BOT = commands.Bot(command_prefix='?', intents=INTENTS)

CHANNEL = int(config('CHANNEL', 0))
URL = config('URL', '')
LOOP_TIME = int(config('LOOP_TIME', 30))

tempo_ultima_noticia = ''


@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}')
    concursos_brasil.start()


@tasks.loop(minutes=LOOP_TIME)
async def concursos_brasil():
    global tempo_ultima_noticia
    GUILD = BOT.get_guild(int(config('GUILD_ID', 0)))
    channel = GUILD.get_channel(CHANNEL)
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    concursos_recentes = soup.select_one('.recentes-container')
    description = []

    if not tempo_ultima_noticia:
        tempo_ultima_noticia = datetime.strptime('17:00', "%H:%M")

    for article in concursos_recentes.children:
        link = article.select_one('a')['href']
        localidade = article.select_one('.sigla').text.strip()
        titulo = article.select_one('.post-title').text.strip()
        tempo = article.select_one('time').text.strip()
        author = article.select_one('span > span').text.strip()

        tempo_article = datetime.strptime(tempo, "%d/%m/%Y às %Hh%M")  # noqa: E501

        if tempo_article < tempo_ultima_noticia:
            continue

        description.append(
            f"## [{localidade} - {titulo}]({link})\n{tempo} por {author}"
        )

    tempo_ultima_noticia = datetime.now()

    time = datetime.now().strftime('%Y-%m-%d %H:%M')

    if len(description) <= 0:
        print('Sem notícias recentes.')
        return

    embed = discord.Embed(
        title=f'📢 Concursos Brasil - Notícias Recentes" [{time}]',  # noqa: E501
        url=URL,
        color=discord.Color.green(),
        description="\n".join(description)
    )

    teste = GUILD.get_role(847909384876195901)

    embed.set_footer(text=f"Mensagem enviada pelo {teste.mention}")
    embed.set_thumbnail(
        url='https://i.ibb.co/KyTkq14/concursos-brasil.jpg'  # noqa: E501
    )

    await channel.send(teste.mention, embed=embed)


BOT.run(TOKEN)
