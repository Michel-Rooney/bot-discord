import io
import sqlite3
from datetime import datetime, timedelta

import db
import discord
import matplotlib.pyplot as plt
from decouple import config
from discord.ext import commands

TOKEN = config('TOKEN', '')

INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix='!', intents=INTENTS)

XP_POINT = int(config('XP_POINT', 1))

GUILD_ID = int(config('GUILD_ID', 0))
CHANNEL_ID = int(config('CHANNEL_ID', 0))

DB = 'db.sqlite3'


@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}')
    db.migrations()


def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def convert_time(time):
    return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')


def calc_xp(total_time):
    # TODO: Colocar para minutos
    xp_per_min = int(total_time.total_seconds())

    xp = 0
    if xp_per_min > 0:
        xp = xp_per_min * XP_POINT

    return xp


@BOT.command(name='xp')
async def xp(ctx):
    member = ctx.author
    channel = ctx.channel

    user = db.get_user(member)
    buffer = criar_grafico(member, user)
    embed, file = criar_embed(member, buffer, user)

    await channel.send(member.mention, embed=embed, file=file)


@BOT.command(name='xp week')
async def xp(ctx):
    member = ctx.author
    channel = ctx.channel

    user = db.get_user(member)
    buffer = criar_grafico(member, user)
    embed, file = criar_embed(member, buffer, user)

    await channel.send(member.mention, embed=embed, file=file)


def total_horas_embed(user):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    total_horas_sum = c.execute('''
        SELECT SUM(total_time) FROM study
        WHERE user = ?
    ''', (user[0],)).fetchone()[0]

    horas, minutos = 0, 0

    if total_horas_sum is not None:
        total_horas = total_horas_sum / 3600
        horas = int(total_horas)
        minutos = int((total_horas - horas) * 60)

    conn.close()

    return horas, minutos


def canal_mais_usa(user):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    canal_db = c.execute('''
        SELECT channel_id, COUNT(channel_id), SUM(total_time) AS occurrences
        FROM study
        WHERE user = ?
        GROUP BY channel_id
        ORDER BY occurrences DESC
        LIMIT 1
    ''', (user[0],)).fetchone()

    guild = BOT.get_guild(GUILD_ID)
    canal = guild.get_channel(canal_db[0])

    horas, minutos = 0, 0

    if canal_db[2] > 0:
        total_horas = canal_db[2] / 3600
        horas = int(total_horas)
        minutos = int((total_horas - horas) * 60)

    c.close()
    return canal, horas, minutos


def criar_embed(member, buffer, user):
    horas, minutos = total_horas_embed(user)
    canal, canal_horas, canal_minutos = canal_mais_usa(user)
    canal_tempo = f'**{canal_horas}h {canal_minutos}min**'

    embed = discord.Embed(
        title=f'Estatísticas semanal de {member.name}',
    )

    embed.add_field(
        name=f'{member.name}, você tem',
        value=f'{int(user[3])} xp 😎',
        inline=True
    )

    embed.add_field(
        name='Tempo total de estudos',
        value=f'{horas}h {minutos}min',
        inline=True
    )

    embed.add_field(
        name='Canal de voz mais conectado 🔊',
        value=f'{canal} - {canal_tempo}',
        inline=False
    )

    embed.set_footer(text=f'{datetime.now().strftime("%d %b %Y %H:%M:%S")}')

    buffer.seek(0)
    file = discord.File(fp=buffer, filename='grafico.png')
    embed.set_image(url='attachment://grafico.png')

    return embed, file


def criar_grafico(member, user, days=6):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    today = datetime.now()
    categorias = []
    valores = []

    for i in range(days, -1, -1):
        dia = today - timedelta(days=i)
        data_formatada = dia.strftime('%Y-%m-%d')
        categorias.append(dia.strftime('%d/%m'))

        total_time_sum = c.execute('''
            SELECT SUM(total_time) FROM study
            WHERE user = ? AND DATE(created_at) = ?
        ''', (user[0], data_formatada)).fetchone()[0]

        if total_time_sum is None:
            valores.append(0)
            continue

        # Mudar para horas
        valor = int(total_time_sum)
        valores.append(valor)

    asdf = c.execute('''
    SELECT
        DATE(created_at) AS dia,
        SUM(total_time) AS total_tempo
    FROM
        study
    WHERE
        DATE(created_at) >= DATE('now', '-40 days') AND
        user = ?
    GROUP BY
        DATE(created_at)
    ORDER BY
        dia;
    ''', (user[0],)).fetchall()
    print(asdf)

    plt.bar(categorias, valores)
    plt.xlabel('Dia')
    plt.ylabel('Horas')
    plt.title(f'Gráfico de Horas Estudadas {today.year} - {member.name}')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plt.clf()
    conn.close()
    return buffer


@BOT.event
async def on_voice_state_update(member, before, after):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    guild = BOT.get_guild(GUILD_ID)

    if before.channel is None and after.channel is not None:
        user = db.get_user(member)

        if not user:
            user = c.execute('''
                INSERT INTO user (discord_id, guild_id, xp)
                VALUES (?, ?, ?)
            ''', (member.id, guild.id, 0))

            conn.commit()
            user = db.get_user(member)

        c.execute('''
            INSERT INTO study (
                user,
                start_time,
                channel_id
            ) VALUES (?, ?, ?)
        ''', (user[0], time_now(), after.channel.id))
        conn.commit()

    elif before.channel is not None and after.channel is None:
        user = db.get_user(member)
        study = db.get_study_by_user(user[0])

        start_time = convert_time(study[2])
        end_time = time_now()
        end_time_converted = convert_time(time_now())
        total_time = end_time_converted - start_time
        xp = calc_xp(total_time)

        c.execute('''
            UPDATE study
            SET end_time = ?,
                total_time = ?,
                xp = ?
            WHERE id = ?
        ''', (end_time, int(total_time.total_seconds()), xp, study[0]))

        c.execute('''
            UPDATE user
            SET xp = ?
            WHERE id = ?
        ''', (user[3] + xp, user[0]))

        conn.commit()

    conn.close()

BOT.run(TOKEN)
