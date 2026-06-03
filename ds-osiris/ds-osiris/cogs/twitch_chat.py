import discord
from discord.ext import commands
import twitchio
from twitchio.ext import commands as twitch_cmds
import os
import asyncio
from iaosiris import ia_osiris, ia_devinette 

class TwitchListener(twitch_cmds.Bot):
    def __init__(self, token, client_id, client_secret):
        super().__init__(
            token=token,
            client_id=client_id,
            client_secret=client_secret,
            prefix="!", 
            initial_channels=[]
        )
        self.defi_en_cours = None 
        self.memoire_twitch = {} 

    async def event_ready(self):
        print(f"[Twitch] 🏴‍☠️ Osiris a jeté l'ancre ! (Connecté : {self.nick})")

    async def event_message(self, message):
        if message.echo:
            return

        msg_lower = message.content.lower().strip()
        auteur = message.author.name.lower()

        if "vice_capitaine_osiris" in msg_lower:
            try:
                if auteur not in self.memoire_twitch:
                    self.memoire_twitch[auteur] = []
                
                if len(self.memoire_twitch[auteur]) >= 4:
                    self.memoire_twitch[auteur] = self.memoire_twitch[auteur][-2:]

                pseudos_capitaine = ["ravastes", "beber", "berkant"]
                
                if auteur in pseudos_capitaine:
                    facon_etre = "Tu es Osiris. Le viewer est ton Capitaine Ravastes (ton créateur). Respect immense. Très court."
                else:
                    facon_etre = f"Tu es Osiris. Le viewer est {message.author.name}. Arrogance et moquerie. Très court."

                reponse = await ia_osiris(
                    message=message.content, 
                    facon_etre=facon_etre, 
                    memoire=self.memoire_twitch[auteur],
                    max_token=100
                )
                
                if reponse:
                    self.memoire_twitch[auteur].append(f"Viewer: {message.content}")
                    self.memoire_twitch[auteur].append(f"Osiris: {reponse}")
                    await message.channel.send(f"@{message.author.name} {reponse}")
            except Exception as e:
                print(f"Erreur discussion Twitch : {e}")

class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_client = TwitchListener(
            os.getenv("TWITCH_CHANNEL_OSIRIS"),
            os.getenv("TWITCH_CLIENT_ID"),
            os.getenv("TWITCH_TOKKEN")
        )
        self.twitch_task = None

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.twitch_task:
            self.twitch_task = self.bot.loop.create_task(self.twitch_client.start())

    @commands.command()
    @commands.is_owner()
    async def aborder(self, ctx, chaine: str):
        """Rejoint le chat d'un streamer"""
        chaine = chaine.lower()
        await ctx.send(f"🏴‍☠️ Abordage de **{chaine}**...")
        try:
            await self.twitch_client.join_channels([chaine])
            await asyncio.sleep(2)
            canal = self.twitch_client.get_channel(chaine)
            if canal:
                await canal.send("Par les mille sabords, Osiris est à bord !")
                await ctx.send(f"✅ Osiris a jeté l'ancre chez **{chaine}** !")
            else:
                await ctx.send(f"⚓ Osiris a rejoint **{chaine}**.")
        except Exception as e:
            await ctx.send(f"❌ Échec : {e}")

    @commands.command()
    @commands.is_owner()
    async def fuir(self, ctx, chaine: str):
        """Quitte le chat et vide la cale"""
        chaine = chaine.lower()
        try:
            canal = self.twitch_client.get_channel(chaine)
            if canal:
                await canal.send("CAPITAINE LE NAVIRE PREND L'EAU, JE DOIS FUIR ! ( bye bye la team )")
            await self.twitch_client.part_channels([chaine])
            self.twitch_client.memoire_twitch.clear()
            await ctx.send(f"💨 Osiris a quitté **{chaine}** et vidé sa mémoire.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

async def setup(bot):
    await bot.add_cog(TwitchCog(bot))