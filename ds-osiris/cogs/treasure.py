import discord
import json
import os
import asyncio
import random
from discord.ext import commands
from iaosiris import ia_osiris

SCORE_FILE = "data/scores.json"

class TreasureHunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chasses_actives = {}

    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_scores(self, scores):
        os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f, indent=2)

    @commands.command(name="chasse_tresor")
    async def lancer_chasse(self, ctx):
        """Lance une recherche de coffre sur le serveur"""
        if ctx.author.id in self.chasses_actives:
            return await ctx.send("Tu as déjà une carte en main ! Trouve le premier coffre avant d'en chercher un autre.")

        salons_possibles = [
            c for c in ctx.guild.text_channels 
            if c.permissions_for(ctx.guild.me).send_messages 
            and c.permissions_for(ctx.author).view_channel   
            and c.permissions_for(ctx.author).send_messages  
            and not any(word in c.name.lower() for word in ["admin", "mod", "staff", "log", "bureau", "commande"])
        ]

        if not salons_possibles:
            return await ctx.send("🏴‍☠️ Toutes les îles sont sous haute surveillance... Impossible de cacher un trésor ici !")

        target_channel = random.choice(salons_possibles)

        await ctx.send("📜 **Osiris déploie un vieux parchemin... le destin se dessine.**")

        prompt_enigme = (
            f"Tu es Osiris, un vieux pirate arrogant. Le trésor est caché dans le salon nommé '{target_channel.name}'. "
            f"Le sujet de ce salon est : '{target_channel.topic if target_channel.topic else 'discuter de tout et de rien'}'. "
            "Crée une énigme de pirate mystérieuse (maximum 3 phrases) qui décrit ce lieu sans citer son nom. "
            "Le joueur doit comprendre de quel salon Discord il s'agit."
        )

        try:
            enigme = await ia_osiris("Enigme de lieu", prompt_enigme, [], 250)
            
            self.chasses_actives[ctx.author.id] = target_channel.id

            await ctx.send(f"🗺️ **La carte de {ctx.author.mention} révèle ces indices :**\n\n*{enigme}*")
            await ctx.send("📍 **Trouve le bon salon et tape `Osiris deterrer` pour prendre le butin !**\n*(Dépêche-toi, tu as 5 minutes !)*")

            await asyncio.sleep(300)
            
            if ctx.author.id in self.chasses_actives:
                del self.chasses_actives[ctx.author.id]
                try:
                    await ctx.author.send("⌛ **La carte s'est effacée !** Tu as été trop lent, le trésor a été déplacé ou pillé par d'autres flibustiers.")
                except:
                    await ctx.send(f"⌛ {ctx.author.mention}, ta carte est devenue illisible. Le trésor a disparu !")

        except Exception as e:
            print(f"Erreur Chasse au trésor : {e}")
            if ctx.author.id in self.chasses_actives:
                del self.chasses_actives[ctx.author.id]

    @commands.command(name="deterrer")
    async def deterrer_coffre(self, ctx):
        """Commande pour réclamer le trésor dans le bon salon"""
        user_id = ctx.author.id
        
        if user_id not in self.chasses_actives:
            return

        target_id = self.chasses_actives[user_id]

        if ctx.channel.id == target_id:
            del self.chasses_actives[user_id]
            
            scores = self.load_scores()
            recompense = 75
            
            user_key = str(ctx.author)
            scores[user_key] = scores.get(user_key, 0) + recompense
            self.save_scores(scores)

            facon = f"Tu es Osiris. Félicite avec arrogance {ctx.author.display_name} d'avoir trouvé le coffre dans le salon {ctx.channel.name}."
            msg_ia = await ia_osiris("Bravo Trésor", facon, [], 150)
            
            await ctx.send(f"💎 **BINGO ! X MARQUE L'EMPLACEMENT !**")
            await ctx.send(msg_ia)
            await ctx.send(f"💰 **+75 doublons** ont été ajoutés à ton coffre !")
        else:
            await ctx.send(f"⛏️ {ctx.author.mention}, tu creuses dans le vide ! Ce n'est pas ici. Cherche encore !", delete_after=10)

async def setup(bot):
    await bot.add_cog(TreasureHunt(bot))