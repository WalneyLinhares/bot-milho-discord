import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from commands.milho import setup_commands
from events.on_message import setup_events

# >>> ADIÇÃO PARA RENDER <<<
from flask import Flask
from threading import Thread

app = Flask(__name__)

# ➜ ROTA NOVA: usada para manter online
@app.route("/wake")
def wake():
    print("alive")
    return "alive"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

web_thread = Thread(target=run_web)
web_thread.start()
# -------------------------

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# Configura comandos e eventos
setup_commands(bot)
setup_events(bot)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Programado por 1Million'))
    print(f"Bot online como {bot.user}")

bot.run(TOKEN)
