import datetime
import random

import discord
from decouple import config
from discord.ext import commands, tasks

TOKEN = config('TOKEN')
GUILD_ID = int(config('GUILD_ID', 0))

LOCK_CHANNEL_ID = int(config('LOCK_CHANNEL_ID', 0))
UTC = int(config('UTC', 1))
ROLE_ID = int(config('ROLE_ID', 0))

H_OPEN = int(config('H_OPEN', 5))
M_OPEN = int(config('M_OPEN', 30))

H_CLOSE = int(config('H_CLOSE', 0))
M_CLOSE = int(config('M_CLOSE', 0))


offset = datetime.timedelta(hours=UTC)
tz = datetime.timezone(offset)

time_to_open = datetime.time(hour=H_OPEN, minute=M_OPEN, tzinfo=tz)
time_to_close = datetime.time(hour=H_CLOSE, minute=M_CLOSE, tzinfo=tz)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

motivational_quotes = [
    "Você é mais forte do que imagina.",
    "Nunca desista dos seus sonhos.",
    "Acredite em si mesmo e tudo será possível.",
    "O sucesso é a soma de pequenos esforços repetidos dia após dia.",
    "A vida começa onde sua zona de conforto termina.",
    "Seja a mudança que você deseja ver no mundo.",
    "Cada dia é uma nova chance para melhorar.",
    "A persistência é o caminho do êxito.",
    "Faça o que você ama e nunca terá que trabalhar um dia na vida.",
    "Seus sonhos não têm data de validade.",
    "Desafios são oportunidades disfarçadas.",
    "Nunca é tarde para ser o que você poderia ter sido.",
    "O sucesso é a soma de pequenos esforços.",
    "Se você pode sonhar, você pode realizar.",
    "Grandes conquistas começam com pequenos passos.",
    "A vitória pertence ao mais persistente.",
    "O único limite para o seu sucesso é a sua mente.",
    "Não espere por uma oportunidade, crie-a.",
    "Acredite que você pode e já está no meio do caminho.",
    "Você não precisa ser grande para começar, mas precisa começar para ser grande.",
    "O caminho para o sucesso é sempre em construção.",
    "Transforme seus obstáculos em oportunidades.",
    "Não conte os dias, faça os dias contarem.",
    "O fracasso é apenas a oportunidade de começar de novo, com mais inteligência.",
    "Seja corajoso. A vida recompensa quem ousa.",
    "O futuro pertence àqueles que acreditam na beleza de seus sonhos.",
    "Cada dia é uma nova oportunidade para mudar sua vida.",
    "A única maneira de fazer um excelente trabalho é amar o que você faz.",
    "A jornada de mil milhas começa com um único passo.",
    "Você é capaz de realizar coisas incríveis."
]

sleep_motivational_quotes = [
    "Uma boa noite de sono é o melhor investimento para um dia produtivo.",
    "Dormir bem é o primeiro passo para acordar com energia e motivação.",
    "O descanso adequado é a chave para uma mente e corpo saudáveis.",
    "Um sono de qualidade é a fundação do sucesso e da felicidade.",
    "Cada boa noite de sono é um passo em direção ao seu melhor eu.",
    "O sono reparador é a melhor forma de recarregar suas energias.",
    "Dormir bem é um ato de autocuidado e amor próprio.",
    "A qualidade do seu sono determina a qualidade do seu dia.",
    "Uma mente descansada é uma mente criativa e produtiva.",
    "Aproveite cada noite de sono como uma oportunidade para se renovar e crescer."
]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    lock_unlock_vip.start()


@tasks.loop(time=[time_to_open, time_to_close])
async def lock_unlock_vip():
    guild = bot.get_guild(int(GUILD_ID))
    channel = guild.get_channel(int(LOCK_CHANNEL_ID))

    vip_role = guild.get_role(ROLE_ID)

    overwrite = channel.overwrites_for(vip_role)
    message = 'Mensagem não carregada. Avisar os moderadores.'
    quote = 'Mensagem não carregada. Avisar os moderadores.'
    color = discord.Color.blue()

    if overwrite.send_messages:
        overwrite.send_messages = False
        quote = random.choice(sleep_motivational_quotes)
        color = discord.Color.purple()

        message = (
            'Canal bloqueado. Boa noite! '
            '**Bora de dormes,** amanhã é outro dia 💤'
        )

    else:
        overwrite.send_messages = True
        quote = random.choice(motivational_quotes)
        color = discord.Color.yellow()

        message = (
            'Canal liberado. Bom dia! '
            '**Foco no papiro!!** 🎯'
        )

    embed = discord.Embed(
        title=message,
        color=color,
        description=quote,
    )

    embed.set_author(name='Bot em evidência [MENSAGEM AUTOMÁTICA]')
    await channel.send(embed=embed)
    await channel.set_permissions(vip_role, overwrite=overwrite)

bot.run(TOKEN)
