import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKKEN_MC = os.getenv("BOTMC")

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="Osiris_MC", intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user} !')

# 4. Une commande de test simple
@bot.command()
async def qui(ctx):
    await ctx.send("Je fais rien, je suis juste un bot !")

# 5. Lancement
bot.run(TOKKEN_MC)
