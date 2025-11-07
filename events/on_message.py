import discord
import time
from discord import Message
from utils.caps_detector import is_caps_lock
from utils.meta_ai_client import perguntar_ia
from config import OWNER_ID, EXEMPT_ROLES

ultimo_aviso_caps = {}
CAPS_COOLDOWN = 5  # segundos

async def is_exempt(member) -> bool:
    """Verifica se o membro é owner, admin ou cargo isento."""
    if member.id == OWNER_ID or member.guild_permissions.administrator:
        return True
    if any(role.id in EXEMPT_ROLES for role in member.roles):
        return True
    return False

async def handle_caps_lock(message):

    if message.guild is None:
        return
    
    # precisa ser member pra ter perms
    if not isinstance(message.author, discord.Member):
        return
    
    # ignorar dono ou admin
    if message.author == message.guild.owner or message.author.guild_permissions.administrator:
        return

    if is_caps_lock(message.content):

        agora = time.time()
        user_id = message.author.id
        ultimo = ultimo_aviso_caps.get(user_id, 0)

        # delete a mensagem sempre
        try:
            await message.delete()
        except discord.NotFound:
            pass

        # envia aviso só se cooldown expirou
        if agora - ultimo >= CAPS_COOLDOWN:
            alert_msg = await message.channel.send(
                f"{message.author.mention}, evite CAPS LOCK! <:ban:1191968282002071663>"
            )
            ultimo_aviso_caps[user_id] = agora
            await alert_msg.delete(delay=5)

        return


async def handle_reply_to_bot(bot, message: Message):
    """Responde automaticamente quando alguém responde ao bot, mantendo contexto."""
    
    # precisa ter referência
    if not message.reference:
        return
    
    try:
        replied_message = await message.channel.fetch_message(message.reference.message_id)
    except:
        return
    
    # só responde se foi o bot que foi respondido
    if replied_message.author != bot.user:
        return
    
    # montar contexto enterprise
    # resumo: meta ai vai saber o que ela falou antes e o que o humano respondeu
    texto = (
        "[CONTEXT=USER_IS_REPLYING_TO_BOT]\n"
        f"[BOT_LAST_MESSAGE]: {replied_message.content}\n"
        f"[USER_REPLY]: {message.content.strip()}"
    )
    
    async with message.channel.typing():
        try:
            resposta = perguntar_ia(
                texto,
                usuario_id=message.author.id,
                usuario_nome=message.author.display_name
            )
            await message.reply(resposta)
        except Exception as e:
            print(f"Erro no reply_auto: {e}")
            await message.reply("Eu buguei tentando continuar o assunto 😵")


def setup_events(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user or not message.guild:
            return

        # Processa comandos primeiro
        await bot.process_commands(message)

        # Modular: reply e CAPS LOCK
        await handle_reply_to_bot(bot, message)
        await handle_caps_lock(message)