import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import openai

load_dotenv()

TOKKEN = os.getenv("BOT_DISCORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
organization = os.getenv("ORGANIZATION")

intents = discord.Intents.all()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="Osiris ", intents=intents)
bot.remove_command('help')

bot.client_ia = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    organization=organization
)

COGS = [
    "cogs.events",
    "cogs.music",
    "cogs.gambling",
    "cogs.admin",
    "cogs.games",
    "cogs.devinette",
    "cogs.sport",
    "cogs.ade",
    "cogs.misc",
    "cogs.stream",
    "cogs.twitch_chat"
]

async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            print(f"Cog chargé : {cog}")
        await bot.start(TOKKEN)

asyncio.run(main())