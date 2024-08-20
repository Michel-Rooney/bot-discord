import discord
from decouple import config
from discord.ext import commands, tasks

TOKEN = config('TOKEN_MOVE_USER', '')  # TOKEN DO BOT
GUILD_ID = config('GUILD_ID_MOVE_USER', '')  # ID DO SERVER

# ORIGEM -> WEBCAM
SOURCE_CHANNEL_ID = config('SOURCE_CHANNEL_ID_MOVE_USER', '')
# DESTINO -> GERAL
TARGET_CHANNEL_ID = config('TARGET_CHANNEL_ID_MOVE_USER', '')
# TEMPO DO LOOP DA VERIFICAÇÃO
LOOP_INTERVAL = int(config('LOOP_INTERVAL_MOVE_USER', 2))


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    move_users.start()


@tasks.loop(minutes=LOOP_INTERVAL)
async def move_users():
    guild = bot.get_guild(int(GUILD_ID))
    source_channel = guild.get_channel(int(SOURCE_CHANNEL_ID))
    target_channel = guild.get_channel(int(TARGET_CHANNEL_ID))

    if source_channel and target_channel:
        for member in source_channel.members:
            if not member.bot:
                if not member.voice.self_video and not member.voice.self_stream:  # noqa: E501
                    await member.move_to(target_channel)
                    await member.send(
                        f'**[ESTUDOS EM EVIDÊNCIA]** Olá {member.name}, ',
                        'o canal **{source_channel.name}** é apenas para ',
                        'câmeras ou streams ligadas. Portanto, você foi ',
                        'movido para sala **{target_channel.name}.**'
                    )
                    print(f'Moved {member.name} to {target_channel.name}')


bot.run(TOKEN)
