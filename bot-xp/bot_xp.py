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
BOT = commands.Bot(command_prefix='?', intents=INTENTS)

XP_POINT = int(config('XP_POINT', 1))

GUILD_ID = int(config('GUILD_ID', 0))
CHANNEL_ID = int(config('CHANNEL_ID', 0))


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
    xp_per_min = int(total_time.total_seconds() / 60)

    xp = 0
    if xp_per_min > 0:
        xp = xp_per_min * XP_POINT

    return xp


@BOT.event
async def on_voice_state_update(member, before, after):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    guild = BOT.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

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

        print(xp)

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

    user = db.get_user(member)
    today = datetime.now()
    categorias = []
    valores = []

    for i in range(6, -1, -1):
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

        valores.append(total_time_sum / 3600)

    plt.bar(categorias, valores)
    plt.xlabel('Dia')
    plt.ylabel('Horas')
    plt.title(f'Gráfico de Horas Estudadas {today.year} - {member.name}')

    # plt.xticks(rotation=30, ha='right')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # await channel.send(file=discord.File(fp=buffer, filename='grafico.png'))

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
        value=f'{int(sum(valores))}',
        inline=True
    )

    embed.set_footer(text=f'{datetime.now().strftime("%d %b %Y %H:%M:%S")}')

    buffer.seek(0)
    file = discord.File(fp=buffer, filename='grafico.png')
    embed.set_image(url='attachment://grafico.png')

    await channel.send(member.mention, embed=embed, file=file)

    plt.clf()
    conn.close()

BOT.run(TOKEN)
