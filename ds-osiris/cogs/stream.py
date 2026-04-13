import discord
from discord.ext import commands, tasks
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_TOKKEN = os.getenv("TWITCH_TOKKEN")


class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot        
        self.twitch_client_id = TWITCH_CLIENT_ID
        self.twitch_client_secret = TWITCH_TOKKEN
        
        # Liste des chaînes Twitch à surveiller (en minuscules)
        self.streamers = ["hideyosh_", "saturnesmile", "flapiix"] 
        
        self.annonce_channel_id = 1491729454068666368 

        self.twitch_token = None
        self.live_streamers = [] # Garde en mémoire qui est en live pour ne pas spammer
        
        self.check_streams.start()

    def cog_unload(self):
        self.check_streams.cancel()

    async def get_twitch_token(self):
        """Récupère le token d'accès pour utiliser l'API Twitch."""
        url = f"https://id.twitch.tv/oauth2/token?client_id={self.twitch_client_id}&client_secret={self.twitch_client_secret}&grant_type=client_credentials"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.twitch_token = data.get("access_token")
                    print("[Stream Cog] Token Twitch généré avec succès.")
                else:
                    print(f"[Stream Cog] Erreur lors de la récupération du token Twitch : {response.status}")

    @tasks.loop(minutes=15)
    async def check_streams(self):
        """Vérifie le statut des streamers."""
        await self.bot.wait_until_ready()
        
        channel = self.bot.get_channel(self.annonce_channel_id)
        if not channel:
            print("[Stream Cog] Salon d'annonce introuvable.")
            return

        # Si on n'a pas de token, on va en chercher un
        if not self.twitch_token:
            await self.get_twitch_token()
            if not self.twitch_token:
                return 

        headers = {
            "Client-ID": self.twitch_client_id,
            "Authorization": f"Bearer {self.twitch_token}"
        }

        # On prépare l'URL avec tous les streamers pour faire une seule requête
        users_query = "&".join([f"user_login={s}" for s in self.streamers])
        url = f"https://api.twitch.tv/helix/streams?{users_query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                
                # Si le token a expiré, on le réinitialise
                if response.status == 401: 
                    self.twitch_token = None
                    return
                
                if response.status == 200:
                    data = await response.json()
                    streams_en_cours = data.get("data", [])
                    
                    # On liste les pseudos de ceux qui sont *actuellement* en live
                    pseudos_en_live = [stream["user_login"].lower() for stream in streams_en_cours]

                    for stream in streams_en_cours:
                        streamer_name = stream["user_login"].lower()
                        
                        if streamer_name not in self.live_streamers:
                            self.live_streamers.append(streamer_name)
                            
                            titre = stream["title"]
                            jeu = stream["game_name"]
                            spectateurs = stream["viewer_count"]
                            image_url = stream["thumbnail_url"].replace("{width}", "1280").replace("{height}", "720")
                            lien = f"https://www.twitch.tv/{stream['user_name']}"

                            embed = discord.Embed(
                                title=f"🔴 {stream['user_name']} est en direct sur Twitch !",
                                description=f"**{titre}**\nJeu : {jeu} | 👁️ {spectateurs} viewers",
                                url=lien,
                                color=discord.Color.purple()
                            )
                            embed.set_image(url=image_url)
                            
                            await channel.send(content=f"AHOY Matelos, un des mes streamers est en live ! {lien} regardez-le !", embed=embed)

                    for streamer in list(self.live_streamers):
                        if streamer not in pseudos_en_live:
                            self.live_streamers.remove(streamer)


async def setup(bot):
    await bot.add_cog(Stream(bot))