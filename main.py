import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from commands.milho import setup_commands
from events.on_message import setup_events

from flask import Flask
from threading import Thread

# =========================================================
# 1. ENV
# =========================================================
load_dotenv()
FASTAPI_WAKE = os.getenv("WAKE_URL")
TOKEN = os.getenv("DISCORD_TOKEN")

# =========================================================
# 2. FLASK SERVER
# =========================================================
app = Flask(__name__)

@app.route("/wake", methods=["GET", "POST"])
def wake():
    print("alive")
    return "alive"


# Sessão será criada dentro da coroutine
http_session = None


async def keep_fastapi_awake():
    global http_session

    # cria a ClientSession só quando o loop estiver ativo
    if http_session is None:
        http_session = aiohttp.ClientSession()

    while True:
        try:
            async with http_session.get(FASTAPI_WAKE) as resp:
                print("[WAKE → FASTAPI]", await resp.text())
        except Exception as e:
            print("[ERRO WAKE FASTAPI]", e)

        await asyncio.sleep(300)


def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# Iniciar Flask
Thread(target=run_web, daemon=True).start()

# Loop asyncio separado
loop = asyncio.new_event_loop()
Thread(target=start_async_loop, args=(loop,), daemon=True).start()

# Iniciar rotina assíncrona no loop
asyncio.run_coroutine_threadsafe(keep_fastapi_awake(), loop)


# =========================================================
# 3. DISCORD BOT
# =========================================================
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

setup_commands(bot)
setup_events(bot)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Programado por 1Million'))
    print(f"Bot online como {bot.user}")

bot.run(TOKEN)