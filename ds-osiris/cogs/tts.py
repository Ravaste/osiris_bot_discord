import discord
import os
import asyncio
from discord.ext import commands
from openai import AsyncOpenAI

client = AsyncOpenAI()

class Intrusion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def parle(self, ctx, membre: discord.Member, *, message: str):
        """Osiris débarque en vocal, hurle un message, et repart."""
        
        if not membre.voice or not membre.voice.channel:
            return await ctx.send(f"Impossible ! {membre.display_name} n'est pas dans un salon vocal. On ne frappe pas un lâche qui se cache.")
        
        canal_vocal = membre.voice.channel

        if len(message) > 200:
            return await ctx.send("Mon souffle a ses limites ! Fais plus court (200 caractères max).")

        fichier_audio = f"temp_tts_{ctx.author.id}.mp3"

        msg_attente = await ctx.send(f"*Préparation des cordes vocales pour traumatiser {membre.display_name}...*")

        try:
            reponse = await client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=message
            )
            reponse.stream_to_file(fichier_audio)

            if ctx.voice_client:
                await ctx.voice_client.disconnect()

            vc = await canal_vocal.connect()

            vc.play(discord.FFmpegPCMAudio(fichier_audio))

            await msg_attente.edit(content=f"**Osiris hurle sur {membre.display_name} :** « {message} »")

            while vc.is_playing():
                await asyncio.sleep(0.5)

            await vc.disconnect()

        except Exception as e:
            print(f"Erreur TTS : {e}")
            await msg_attente.edit(content="Mes cordes vocales m'ont lâché. Erreur système.")
            if ctx.voice_client:
                await ctx.voice_client.disconnect()

        finally:
            if os.path.exists(fichier_audio):
                os.remove(fichier_audio)


async def setup(bot):
    await bot.add_cog(Intrusion(bot))