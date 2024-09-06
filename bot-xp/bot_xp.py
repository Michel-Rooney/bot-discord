import io
import sqlite3
from datetime import datetime, timedelta
from typing import Literal, Optional

import db
import discord
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from decouple import config
from discord.ext import commands

TOKEN = config('TOKEN', '')

INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix='!b3e ', intents=INTENTS)

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


def calc_xp(member, total_time):
    # TODO: Colocar para minutos
    xp_point = int(config('XP_POINT', 1))
    xp_per_min = int(total_time.total_seconds())

    if member.premium_since is not None:
        xp_point = xp_point * 1.5

    xp = 0
    if xp_per_min > 0:
        xp = xp_per_min * xp_point

    return xp


class MemberConverter(commands.MemberConverter):
    async def convert(self, ctx, argument):
        print(ctx)
        print(argument)
        return await super().convert(ctx, argument)


@BOT.command(name='xp')
async def xp(ctx, offset: Literal['day', 'week', 'month', 'year'] = 'week', member_user: MemberConverter = ''):
    member = ctx.author
    channel = ctx.channel

    user = db.get_user(member_user)
    buffer = criar_grafico(member, user, offset)
    embed, file = criar_embed(member, member_user, buffer, user, offset)

    await channel.send(member.mention, embed=embed, file=file)


@BOT.command(name='rank')
async def rank(ctx):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    member = ctx.author
    channel = ctx.channel

    users_rank = '''
        WITH RankedUsers AS (
            SELECT
                id,
                discord_id,
                xp,
                RANK() OVER (ORDER BY xp DESC) AS position
            FROM user
        )
        SELECT *
        FROM RankedUsers
        LIMIT 5
    '''

    user_position = user_position_rank(member)
    users_position = c.execute(users_rank).fetchall()

    rank_users_embed = []
    for user in users_position:
        user_discord = ctx.guild.get_member(user[1])
        user_mention = user[1]

        if user_discord is not None:
            user_mention = user_discord.mention

        rank_users_embed.append(
            f'#{user[3]} | {user_mention} - XP: `{int(user[2])}`'
        )

    user_rank_discord = ctx.guild.get_member(user_position[1])
    message = (
        f'**#{user_position[3]} | {user_rank_discord.mention} '
        f'- XP: `{int(user[2])}`**'
    )
    rank_users_embed.append(message)

    embed = discord.Embed(
        title="📋 Rank do servidor"
    )

    embed.add_field(
        name='🎙Top 5 - Voz',
        value='\n'.join(rank_users_embed),
        inline=False,
    )

    c.close()
    await channel.send(member.mention, embed=embed)


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


def user_position_rank(member):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    user = db.get_user(member)

    user_rank = '''
        WITH RankedUsers AS (
            SELECT
                id,
                discord_id,
                xp,
                RANK() OVER (ORDER BY xp DESC) AS position
            FROM user
        )
        SELECT *
        FROM RankedUsers
        WHERE id = ?;
    '''

    user_position = c.execute(user_rank, (user[0],)).fetchone()
    c.close()

    return user_position


def criar_embed(member, member_user, buffer, user, offset='week'):
    horas, minutos = total_horas_embed(user)
    canal, canal_horas, canal_minutos = canal_mais_usa(user)
    canal_tempo = f'**{canal_horas}h {canal_minutos}min**'

    user_position = user_position_rank(member)

    match offset:
        case 'day':
            title_day = 'do dia'
        case 'week':
            title_day = 'semanal'
        case 'month':
            title_day = 'mensal'
        case 'year':
            title_day = 'anual'

    embed = discord.Embed(
        title=f'Estatísticas {title_day} de {member_user.name}',
    )

    embed.add_field(
        name=f'{member_user.name}, você tem',
        value=f'{int(user[3])} xp 😎',
        inline=True
    )

    embed.add_field(
        name='Tempo total de estudos',
        value=f'{horas}h {minutos}min',
        inline=True
    )

    embed.add_field(
        name='Posição no rank',
        value=f'#{user_position[3]}',
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


def dados_grafico(user, days=6):
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

        # TODO: Mudar para horas
        valor = int(total_time_sum)
        valores.append(valor)

    conn.close()
    return categorias, valores


def dados_grafico_year(user, months=11):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    today = datetime.now()
    categorias = []
    valores = []

    for i in range(months, -1, -1):
        dia = today - relativedelta(months=i)
        data_formatada = dia.strftime('%Y-%m')
        categorias.append(dia.strftime('%m/%Y'))

        total_time_sum = c.execute('''
            SELECT SUM(total_time) FROM study
            WHERE user = ? AND strftime('%Y-%m', created_at) = ?
        ''', (user[0], data_formatada)).fetchone()[0]

        if total_time_sum is None:
            valores.append(0)
            continue

        # TODO: Mudar para horas
        valor = int(total_time_sum)
        valores.append(valor)

    conn.close()
    return categorias, valores


def criar_grafico(member, user, offset='week'):
    today = datetime.now()

    match offset:
        case 'day':
            categorias, valores = dados_grafico(user, days=1)
        case 'week':
            categorias, valores = dados_grafico(user, days=6)
        case 'month':
            categorias, valores = dados_grafico(user, days=29)
        case 'year':
            categorias, valores = dados_grafico_year(user, months=11)

    plt.bar(categorias, valores)
    plt.xlabel('Dia')
    plt.ylabel('Horas')
    plt.title(f'Gráfico de Horas Estudadas {today.year} - {member.name}')

    plt.xticks(rotation=45, fontsize=6)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(1)

    plt.clf()
    return buffer


@ BOT.event
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
        xp = calc_xp(member, total_time)

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
