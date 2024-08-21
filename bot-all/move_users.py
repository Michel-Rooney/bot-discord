from decouple import config
from discord.ext import tasks
from utils import msg_time

MOVE_USER_LOOP_INTERVAL_MIN = int(config('MOVE_USER_LOOP_INTERVAL_MIN', 2))

MOVE_USER_SOURCE_CHANNEL_ID = int(config('MOVE_USER_SOURCE_CHANNEL_ID', 0))
MOVE_USER_TARGET_CHANNEL_ID = int(config('MOVE_USER_TARGET_CHANNEL_ID', 0))


@tasks.loop(minutes=MOVE_USER_LOOP_INTERVAL_MIN)
async def move_users(BOT, GUILD_ID):
    guild = BOT.get_guild(GUILD_ID)
    source_channel = guild.get_channel(MOVE_USER_SOURCE_CHANNEL_ID)
    target_channel = guild.get_channel(MOVE_USER_TARGET_CHANNEL_ID)

    if (not source_channel) or (not target_channel):
        print(
            f'{msg_time()} MOVE_USER: SOURCE_CHANNEL',
            'OU TARGET_CHANNEL INVÁLIDO.'
        )
        return

    for member in source_channel.members:
        if member.bot:
            print(
                '{msg_time()} MOVE_USER: Bot',
                f'{member.name} ignorado no move_users.'
            )
            continue

        if member.voice.self_video or member.voice.self_stream:
            continue

        try:
            await member.move_to(target_channel)

            message = (
                f'**[MODERAÇÃO ESTUDOS EM EVIDÊNCIA]** Olá **{member.name}**,'
                'o canal **"(WEBCAM OU TELA ON)"** é apenas para câmeras ou'
                'streams ligadas. Portanto, você foi movido para sala'
                '**"GERAL"**.'
            )
            await member.send(message)

            print(
                f'{msg_time()} MOVE_USER: Moved',
                f'{member.name} to {target_channel.name}'
            )
        except Exception as e:
            print(
                f'{msg_time()} MOVE_USER: ERRO AO ENVIAR',
                f'MENSAGEM: {member.name}\n {e}'
            )
