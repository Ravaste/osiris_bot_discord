import discord
import asyncio
import re
import os
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
        try:
            if self.queues.get(ctx.guild.id):
                link = self.queues[ctx.guild.id].pop(0)
                await self.jukebox(ctx, link=link)
        except Exception as e:
            print(f"Erreur play_next : {e}")

    def make_after_playing(self, voice_client):
        """Crée le callback after_playing avec le bon voice_client"""
        def after_playing(error):
            if error:
                print(f"Erreur lors de la lecture : {error}")
            try:
                fut = voice_client.disconnect()
                self.bot.loop.create_task(fut)
            except Exception as e:
                print(f"Erreur déconnexion after_playing : {e}")
        return after_playing

    async def get_voice_client(self, message):
        """Récupère ou crée un voice client pour l'auteur du message"""
        if not message.author.voice or not message.author.voice.channel:
            return None
        channel = message.author.voice.channel
        voice_client = message.guild.voice_client
        try:
            if not voice_client:
                voice_client = await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
            return voice_client
        except Exception as e:
            print(f"Erreur connexion vocale : {e}")
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if "on silence" in message.content.lower():
            try:
                await message.channel.send("LE GRAND RABAH")
                await message.channel.send(file=discord.File("gif/on_silence_rabah.png"))
                voice_client = await self.get_voice_client(message)
                if voice_client:
                    audio = FFmpegPCMAudio('musique/on_silence.m4a', **ffmpeg_options_debase)
                    voice_client.play(
                        PCMVolumeTransformer(audio, volume=100),
                        after=self.make_after_playing(voice_client)
                    )
            except Exception as e:
                print(f"Erreur on silence : {e}")

        if "osiris mahoraga" in message.content.lower() or "osiris makora" in message.content.lower():
            try:
                if not hasattr(self.bot, 'heure_verrouille'):
                    self.bot.heure_verrouille = datetime.now()

                if datetime.now() >= self.bot.heure_verrouille:
                    await message.channel.send("Sacred treasure swing and ring ring")
                    try:
                        await message.channel.send(file=discord.File("gif/invoc.gif"))
                    except Exception:
                        pass
                    await message.channel.send("Divergent Sila Divine General")
                    await message.channel.send("Mahoraga")
                    try:
                        await message.channel.send(file=discord.File('gif/mahoraga.gif'))
                    except Exception:
                        pass

                    voice_client = await self.get_voice_client(message)
                    if voice_client:
                        voice_client.play(
                            discord.FFmpegPCMAudio('musique/mahoraga.mp3', **ffmpeg_options_debase),
                            after=self.make_after_playing(voice_client)
                        )
                    self.bot.heure_verrouille = datetime.now() + timedelta(minutes=30)
                else:
                    await message.channel.send("Le rituel n'est pas disponible")
            except Exception as e:
                print(f"Erreur mahoraga : {e}")

        if "Osiris prepare le Rituel du Général Divin" in message.content:
            try:
                if message.author.guild_permissions.administrator:
                    self.bot.heure_verrouille = datetime.now()
                    await message.channel.send("Les préparatives pour le Rituel du Général Divin sont prete")
                else:
                    await message.channel.send("Le Rituel demande des ressources trop puissante pour toi")
            except Exception as e:
                print(f"Erreur rituel : {e}")

        if "Gogeta" in message.content:
            try:
                await message.channel.send("GOGETA ?!")
                await message.channel.send("L'ANGE NEE EN ENFER ?!")
                try:
                    await message.channel.send(file=discord.File("gif/gogeta-blue-metadinha.gif"))
                except Exception:
                    pass
                await message.channel.send("GOATGETA !")
                try:
                    await message.channel.send(file=discord.File("gif/dbgt-dragon-ball-gt.gif"))
                except Exception:
                    pass
                await message.channel.send("*Gogeta > Vegeto*")
            except Exception as e:
                print(f"Erreur Gogeta : {e}")

    @commands.command()
    async def tg(self, ctx):
        try:
            voice_client = ctx.guild.voice_client
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
                await ctx.send("Azy")
            else:
                await ctx.send("MAIS TOI TG, ARRACHE TAS GRAND MERE D'ICI")
        except Exception as e:
            print(f"Erreur tg : {e}")

    @commands.command()
    async def dj(self, ctx, musique: int = 0):
        """Laisse cette douce musique venir"""
        try:
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

            if not os.path.isfile(path):
                await ctx.send("Le fichier n'existe pas!")
                return

            voice_client.play(
                discord.FFmpegPCMAudio(path, **ffmpeg_options_debase),
                after=self.make_after_playing(voice_client)
            )
            await ctx.send(f"Musique : {nom}")
        except Exception as e:
            print(f"Erreur dj : {e}")
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def algebredeboole(self, ctx):
        try:
            if not ctx.author.voice:
                await ctx.send("Tu n'es pas dans un canal vocal!")
                return
            voice_client = ctx.guild.voice_client
            channel = ctx.author.voice.channel
            if not voice_client:
                voice_client = await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
            audio = FFmpegPCMAudio('musique/Lalgebra_de_bool.m4a', **ffmpeg_options_debase)
            voice_client.play(
                PCMVolumeTransformer(audio, volume=100),
                after=self.make_after_playing(voice_client)
            )
        except Exception as e:
            print(f"Erreur algebredeboole : {e}")
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def OH(self, ctx):
        try:
            if not ctx.author.voice:
                await ctx.send("Tu n'es pas dans un canal vocal!")
                return
            voice_client = ctx.guild.voice_client
            channel = ctx.author.voice.channel
            if not voice_client:
                voice_client = await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
            audio = FFmpegPCMAudio('musique/oh.mp3', **ffmpeg_options_debase)
            voice_client.play(
                PCMVolumeTransformer(audio, volume=100),
                after=self.make_after_playing(voice_client)
            )
        except Exception as e:
            print(f"Erreur OH : {e}")
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command(name="jukebox")
    async def jukebox(self, ctx, *, link):
        log = self.bot.get_channel(1123295747601870891)
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
        except Exception as e:
            print(f"Erreur connexion jukebox : {e}")

        try:
            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({'search_query': link})
                content = urllib.request.urlopen(youtube_results_url + query_string)
                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
                if not search_results:
                    await ctx.send("❌ Aucun résultat trouvé.")
                    return
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
            print(f"Erreur jukebox : {e}")
            if log:
                await log.send(f"Erreur jukebox : {e}")

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
            print(f"Erreur pause : {e}")
            if log:
                await log.send(f"Erreur pause : {e}")

    @commands.command(name="resume")
    async def resume(self, ctx):
        log = self.bot.get_channel(1123295747601870891)
        try:
            self.voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(f"Erreur resume : {e}")
            if log:
                await log.send(f"Erreur resume : {e}")

    @commands.command(name="skip")
    async def skip(self, ctx):
        log = self.bot.get_channel(1123295747601870891)
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send("Je fais ca")
        except Exception as e:
            print(f"Erreur skip : {e}")
            if log:
                await log.send(f"Erreur skip : {e}")

    @commands.command(name="volume")
    async def volume(self, ctx, volume):
        await ctx.send("Pour l'instant j'ai rien ici sert a r de forcer")

async def setup(bot):
    await bot.add_cog(Music(bot))