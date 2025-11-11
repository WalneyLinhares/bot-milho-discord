from discord.ext import commands
from utils.ai_client import perguntar_ia

def setup_commands(bot: commands.Bot):
    
    @bot.command(aliases=["m"])
    async def milho(ctx: commands.Context, *, pergunta: str = None):
        """Comando principal do bot, responde usando a IA."""
        async with ctx.typing():
            try:
                if not pergunta:
                    await ctx.reply("Você não escreveu nada para eu responder!")
                    return

                resposta = perguntar_ia(
                    pergunta.strip(),
                    usuario_id=ctx.author.id,
                    usuario_nome=ctx.author.display_name
                )
                await ctx.reply(resposta)
            except Exception as e:
                print(f"Erro no comando !milho: {e}")
                await ctx.reply("Ocorreu um erro ao tentar responder.")