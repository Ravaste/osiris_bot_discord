import discord
import asyncio
import re
import yt_dlp
import urllib.parse
import urllib.request
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from datetime import datetime, timedelta
from pathlib import Path

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
}
ffmpeg_options_debase = {'options': '-vn'}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='

PIRATE_INSTRUCTIONS = (
    "Parle en français, avec une voix grave et rocailleuse, comme un vieux capitaine pirate. "
    "Utilise un ton chaleureux, théâtral et joyeux. Fais des pauses dramatiques. "
    "Ajoute des expressions de marin comme 'harr harr', 'par mille sabords', ou "
    "'que le grand crabe m'emporte !'. Fais rouler les 'r' et donne un rythme ondulant, "
    "comme le ressac des vagues."
)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.speak_lock = asyncio.Lock()

    async def play_next(self, ctx):
        if self.queues.get(ctx.guild.id):
            link = self.queues[ctx.guild.id].pop(0)
            await self.jukebox(ctx, link=link)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        def after_playing(error):
            if error:
                print(f"Erreur lors de la lecture : {error}")
            fut = voice_client.disconnect()
            self.bot.loop.create_task(fut)

        if "on silence" in message.content.lower():
            await message.channel.send("LE GRAND RABAH")
            await message.channel.send(file=discord.File("gif/on_silence_rabah.png"))
            voice_client = message.guild.voice_client
            channel = message.author.voice.channel
            if not voice_client:
                voice_client = await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
            audio = FFmpegPCMAudio('musique/on_silence.m4a', **ffmpeg_options_debase)
            voice_client.play(PCMVolumeTransformer(audio, volume=100), after=after_playing)

        if "osiris mahoraga" in message.content.lower() or "osiris makora" in message.content.lower():
            if not hasattr(self.bot, 'heure_verrouille'):
                self.bot.heure_verrouille = datetime.now()

            if datetime.now() >= self.bot.heure_verrouille:
                await message.channel.send("Sacred treasure swing and ring ring")
                await message.channel.send(file=discord.File("gif/invoc.gif"))
                await message.channel.send("Divergent Sila Divine General")
                await message.channel.send("Mahoraga")
                await message.channel.send(file=discord.File('gif/mahoraga.gif'))

                voice_client = message.guild.voice_client
                channel = message.author.voice.channel
                if not voice_client:
                    voice_client = await channel.connect()
                elif voice_client.channel != channel:
                    await voice_client.move_to(channel)

                voice_client.play(
                    discord.FFmpegPCMAudio('musique/mahoraga.mp3', **ffmpeg_options_debase),
                    after=after_playing
                )
                self.bot.heure_verrouille = datetime.now() + timedelta(minutes=30)
            else:
                await message.channel.send("Le rituel n'est pas disponible")

        if "Osiris prepare le Rituel du Général Divin" in message.content:
            if message.author.guild_permissions.administrator:
                self.bot.heure_verrouille = datetime.now()
                await message.channel.send("Les préparatives pour le Rituel du Général Divin sont prete")
            else:
                await message.channel.send("Le Rituel demande des ressources trop puissante pour toi")

        if "Gogeta" in message.content:
            await message.channel.send("GOGETA ?!")
            await message.channel.send("L'ANGE NEE EN ENFER ?!")
            await message.channel.send(file=discord.File("gif/gogeta-blue-metadinha.gif"))
            await message.channel.send("GOATGETA !")
            await message.channel.send(file=discord.File("gif/dbgt-dragon-ball-gt.gif"))
            await message.channel.send("*Gogeta > Vegeto*")

    @commands.command()
    async def tg(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("Azy")
        else:
            await ctx.send("MAIS TOI TG, ARRACHE TAS GRAND MERE D'ICI")

    @commands.command()
    async def dj(self, ctx, musique: int = 0):
        """Laisse cette douce musique venir"""
        if not ctx.author.voice:
            await ctx.send("Tu n'es pas dans un canal vocal!")
            return

        channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client
        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        fichiers = {
            0: ('musique/ardor.mp3', "Soundscape to Ardor"),
            1: ('musique/sparking.mp3', "Sparking Zero Menu Theme"),
            2: ('musique/Nameless.mp3', "Pride of a Nameless Hunter"),
        }

        if musique not in fichiers:
            await ctx.send("Nope musique indisponible")
            return

        path, nom = fichiers[musique]

        import os
        if not os.path.isfile(path):
            await ctx.send("Le fichier n'existe pas!")
            return

        def after_playing(error):
            if error:
                print(f"Erreur lors de la lecture : {error}")
            fut = voice_client.disconnect()
            self.bot.loop.create_task(fut)

        voice_client.play(
            discord.FFmpegPCMAudio(path, **ffmpeg_options_debase),
            after=after_playing
        )
        await ctx.send(f"Musique : {nom}")

    @commands.command()
    async def algebredeboole(self, ctx):
        def after_playing(error):
            if error:
                print(f"Erreur lors de la lecture : {error}")
            fut = voice_client.disconnect()
            self.bot.loop.create_task(fut)

        voice_client = ctx.guild.voice_client
        channel = ctx.author.voice.channel
        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        audio = FFmpegPCMAudio('musique/Lalgebra_de_bool.m4a', **ffmpeg_options_debase)
        voice_client.play(PCMVolumeTransformer(audio, volume=100), after=after_playing)

    @commands.command()
    async def OH(self, ctx):
        def after_playing(error):
            if error:
                print(f"Erreur lors de la lecture : {error}")
            fut = voice_client.disconnect()
            self.bot.loop.create_task(fut)

        voice_client = ctx.guild.voice_client
        channel = ctx.author.voice.channel
        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        audio = FFmpegPCMAudio('musique/oh.mp3', **ffmpeg_options_debase)
        voice_client.play(PCMVolumeTransformer(audio, volume=100), after=after_playing)

    @commands.command(name="jukebox")
    async def jukebox(self, ctx, *, link):
        log = self.bot.get_channel(1123295747601870891)

        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
        except Exception as e:
            print(e)
            await log.send(str(e))

        try:
            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({'search_query': link})
                content = urllib.request.urlopen(youtube_results_url + query_string)
                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
                link = youtube_watch_url + search_results[0]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            self.voice_clients[ctx.guild.id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx), self.bot.loop
                )
            )
        except Exception as e:
            print(e)
            await log.send(str(e))

    @commands.command(name="ajoute")
    async def ajoute(self, ctx, *, url):
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(url)
        await ctx.send("Il arrive ensuite mec")

    @commands.command(name="efface")
    async def efface(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send("Derniere musique donc ?")
        else:
            await ctx.send("Il y a rien mec")

    @commands.command(name="pause")
    async def pause(self, ctx):
        log = self.bot.get_channel(1123295747601870891)
        try:
            self.voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)
            await log.send(str(e))

    @commands.command(name="resume")
    async def resume(self, ctx):
        log = self.bot.get_channel(1123295747601870891)
        try:
            self.voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)
            await log.send(str(e))

    @commands.command(name="skip")
    async def skip(self, ctx):
        log = self.bot.get_channel(1123295747601870891)
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send("Je fais ca")
        except Exception as e:
            print(e)
            await log.send(str(e))

    @commands.command(name="volume")
    async def volume(self, ctx, volume):
        await ctx.send("Pour l'instant j'ai rien ici sert a r de forcer")

    @commands.command(name="parle")
    async def parle(self, ctx, *, texte: str):
        """Fais parler Osiris : Osiris parle <ton texte>"""
        if self.speak_lock.locked():
            await ctx.send("D'ou tu te permet de me couper la parole ? Je suis pas un bot con fdp")
            return

        async with self.speak_lock:
            nom_fichier = Path("speech_pirate.mp3")

            try:
                response = await self.bot.client_ia.audio.speech.create(
                    model="tts-1",
                    voice="onyx",
                    input=texte,
                    instructions=PIRATE_INSTRUCTIONS,
                )
                nom_fichier.write_bytes(response.content)

                if ctx.author.voice and ctx.author.voice.channel:
                    channel = ctx.author.voice.channel
                    vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
                    if not vc or not vc.is_connected():
                        vc = await channel.connect()

                    source = discord.FFmpegPCMAudio(str(nom_fichier))
                    vc.play(source)

                    while vc.is_playing():
                        await asyncio.sleep(0.5)

                    await vc.disconnect()
                else:
                    await ctx.send("Je ne compte pas parler seul ! C'est toi le schisophrène pas moi !")

            except Exception as e:
                await ctx.send(f"Oups j'ai un peu merder ||{e}||")

            finally:
                if nom_fichier.exists():
                    nom_fichier.unlink()


async def setup(bot):
    await bot.add_cog(Music(bot))