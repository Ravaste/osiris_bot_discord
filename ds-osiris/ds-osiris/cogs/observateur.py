import discord
import random
import io
from discord.ext import commands, tasks
from iaosiris import ia_osiris

class Observateur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.juge_activite.start()
        self.log_channel = self.bot.get_channel(1123295747601870891)

    def cog_unload(self):
        self.juge_activite.cancel()
    
    @tasks.loop(hours=4, minutes=23)
    async def juge_activite(self):
        try:
            await self.log_channel.send("Osiris scrute les activités de l'équipage à la recherche de cibles potentielles pour ses moqueries...")

            CIBLES_AUTORISEES = ["ravaste", "labaguette4632", "._nyxveil_.", "_liot_t", "cha.mallow"] 

            membres_actifs = []
            for guild in self.bot.guilds:
                for member in guild.members:
                    nom_global = member.name.lower()
                    nom_serveur = member.display_name.lower() if member.display_name else ""

                    if not member.bot and (nom_global in CIBLES_AUTORISEES or nom_serveur in CIBLES_AUTORISEES) and member.activities:
                        membres_actifs.append(member)

            if not membres_actifs:
                await self.log_channel.send("Aucun membre actif avec une activité détectée parmi les cibles autorisées. Osiris retourne à sa vigie pour l'instant.")
                return
            
            cible = random.choice(membres_actifs)
            activite = random.choice(cible.activities)
            contexte_activite = ""
            
            await self.log_channel.send(f"Osiris observe {cible.display_name}. Activité détectée : {activite.name}")

            if isinstance(activite, discord.Spotify):
                contexte_activite = f"écoute la musique '{activite.title}' de l'artiste '{activite.artist}' sur Spotify."
                
            elif isinstance(activite, discord.Streaming):
                contexte_activite = f"fait le pitre en live sur '{activite.platform}' sur '{activite.game}'."
                
            elif isinstance(activite, discord.CustomActivity):
                texte = activite.name if activite.name else ""
                emoji = activite.emoji if activite.emoji else ""
                statut = f"{emoji} {texte}".strip()
                if not statut:
                    statut = "un statut vide et inutile"
                contexte_activite = f"affiche fièrement ce statut personnalisé pathétique : '{statut}'."
                
            elif isinstance(activite, discord.Game):
                contexte_activite = f"gâche sa vie sur le jeu '{activite.name}'."
                
            elif isinstance(activite, discord.Activity):
                if activite.type == discord.ActivityType.listening:
                    contexte_activite = f"écoute '{activite.name}'."
                elif activite.type == discord.ActivityType.watching:
                    contexte_activite = f"regarde '{activite.name}'."
                elif activite.type == discord.ActivityType.competing:
                    contexte_activite = f"participe à la compétition '{activite.name}'."
                else:
                    details = activite.details if hasattr(activite, 'details') and activite.details else ""
                    contexte_activite = f"est en train d'utiliser : '{activite.name}' ({details})."
            else:
                nom_obscur = getattr(activite, 'name', 'quelque chose d\'incompréhensible')
                contexte_activite = f"fait une activité tellement bizarre qu'elle s'appelle : '{nom_obscur}'."

            await self.log_channel.send(f"Osiris va juger {cible.display_name} : {contexte_activite}")
            
            prompt_juge = (
                f"Tu es Osiris le pirate. Tu épies l'équipage. Tu viens de remarquer que le misérable '{cible.display_name}' {contexte_activite} "
                "Moque-toi de ce qu'il est en train de faire de manière cinglante et agressive, en UNE ou DEUX phrases max. "
                "Que ce soit une musique, un jeu, un film, un logiciel (comme coder sur Visual Studio), ou un simple statut textuel ridicule, détruis-le."
            )

            roast = await ia_osiris("Juge cette activité.", prompt_juge, [], 150)
            
            canal_taverne = self.bot.get_channel(1342155918309199981) 
            if canal_taverne:
                await canal_taverne.send(roast)

        except Exception as e:
            await self.log_channel.send(f"Osiris a rencontré une tempête dans son cerveau IA et n'a pas pu juger l'activité cette fois. {e}")
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