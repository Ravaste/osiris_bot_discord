import discord
import random
import io
from discord.ext import commands, tasks
from iaosiris import ia_osiris

class Observateur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.juge_activite.start()

    def cog_unload(self):
        self.juge_activite.cancel()

    @tasks.loop(hours=1, minutes=30)
    async def juge_activite(self):
        try:
            membres_actifs = []
            for guild in self.bot.guilds:
                for member in guild.members:
                    if not member.bot and member.activities:
                        membres_actifs.append(member)

            if not membres_actifs:
                return

            cible = random.choice(membres_actifs)
            activite = cible.activities
            contexte_activite = ""

            if isinstance(activite, discord.Spotify):
                contexte_activite = f"écoute la musique '{activite.title}' de l'artiste '{activite.artist}' sur Spotify."
            elif isinstance(activite, discord.Game) or isinstance(activite, discord.Activity):
                contexte_activite = f"joue au jeu '{activite.name}'."
            else:
                return 

            prompt_juge = (
                f"Tu es Osiris le pirate. Tu épies l'équipage. Tu viens de remarquer que le misérable '{cible.display_name}' {contexte_activite} "
                "Moque-toi de ses goûts musicaux ou de son addiction à ce jeu en UNE ou DEUX phrases max. Sois cinglant et agressif."
            )

            roast = await ia_osiris("Juge cette activité.", prompt_juge, [], 150)
            
            canal_taverne = self.bot.get_channel(1342155918309199981) 
            if canal_taverne:
                await canal_taverne.send(f"**Osiris vous observe...**\n{cible.mention} {roast}")

        except Exception as e:
            print(f"Erreur juge activité : {e}")

    @juge_activite.before_loop
    async def before_juge_activite(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.attachments:
            for attachment in message.attachments:
                if attachment.is_voice_message():
                    try:
                        await message.add_reaction("👂")
                        
                        audio_bytes = await attachment.read()
                        audio_file = io.BytesIO(audio_bytes)
                        audio_file.name = "voice_message.ogg"

                        # Demander la transcription à l'API Whisper
                        transcript = await self.bot.client_ia.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                        texte_transcrit = transcript.text

                        prompt_sys = (
                            "Tu es Osiris le pirate. Voici la retranscription exacte d'un message vocal bégayé par un membre de l'équipage. "
                            "Fais un commentaire moqueur, condescendant ou drôle sur ce qu'il vient de dire, ou sur le fait qu'il n'articule pas. "
                            "Une ou deux phrases maximum."
                        )
                        
                        avis_osiris = await ia_osiris(
                            message=f"Le marin a dit : '{texte_transcrit}'", 
                            facon_etre=prompt_sys, 
                            memoire=[], 
                            max_token=200
                        )

                        reponse_finale = (
                            f"**Transcription du rat d'eau douce :**\n> *« {texte_transcrit} »*\n\n"
                            f"**L'avis d'Osiris :** {avis_osiris}"
                        )
                        await message.reply(reponse_finale)

                    except Exception as e:
                        print(f"Erreur transcription vocale : {e}")
                        await message.reply("🏴Mon perroquet est sourd aujourd'hui, je n'ai pas pu décrypter tes grognements.")
                    return 

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        if after.channel is not None and before.channel != after.channel:
            if len(after.channel.members) == 1:
                
                canal_taverne = self.bot.get_channel(1342155918309199981) 
                
                if canal_taverne:
                    prompt_voc = (
                        f"Tu es Osiris le pirate. Le joueur '{member.display_name}' vient de rejoindre le salon vocal '{after.channel.name}' tout seul. "
                        "Lâche-lui une punchline cinglante et TRÈS COURTE (1 phrase) pour te moquer de lui. "
                        "Insinue qu'il est au chômage, qu'il n'a pas de vie sociale, ou qu'il attend ses amis comme un misérable chien abandonné sur le quai."
                    )
                    
                    try:
                        roast_voc = await ia_osiris("Juge son arrivée en vocal.", prompt_voc, [], 150)
                        
                        await canal_taverne.send(f"🎙️ {member.mention} {roast_voc}")
                    except Exception as e:
                        print(f"Erreur vocale Osiris : {e}")

async def setup(bot):
    await bot.add_cog(Observateur(bot))