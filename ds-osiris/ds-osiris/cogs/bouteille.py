import discord
import random
import os
import json
from discord.ext import commands

BOUTEILLES_FILE = "data/bouteilles.json"

def charger_bouteilles():
    if os.path.exists(BOUTEILLES_FILE):
        try:
            with open(BOUTEILLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def sauvegarder_bouteilles(bouteilles):
    with open(BOUTEILLES_FILE, "w", encoding="utf-8") as f:
        json.dump(bouteilles, f, indent=2, ensure_ascii=False)

class Bouteille(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bouteille(self, ctx, *, message: str):
        """Envoie un message anonyme dans une bouteille à la mer (En MP uniquement)"""
        if ctx.guild is not None:
            try:
                await ctx.message.delete()
            except:
                pass
            return await ctx.author.send("Idiot ! Si tu veux jeter une bouteille anonyme, fais-le ICI en Message Privé avec la commande `Osiris bouteille [ton message]` ! Sinon tout l'équipage va te démasquer.")

        if len(message) < 5:
            return await ctx.send("Ton bout de parchemin est trop petit, écris quelque chose de plus consistant.")

        bouteilles = charger_bouteilles()
        bouteilles.append(message)
        sauvegarder_bouteilles(bouteilles)

        await ctx.send("*Plouf !* Ta bouteille a bien été jetée à la mer. Elle s'échouera sur le pont quand l'équipage s'y attendra le moins...")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        TAVERNE_ID = 1342155918309199981

        if message.channel.id == TAVERNE_ID:
            bouteilles = charger_bouteilles()
            
            if bouteilles and random.randint(1, 1000) == 1:
                bouteille_trouvee = bouteilles.pop(0)
                sauvegarder_bouteilles(bouteilles)

                intro = (
                    f"*Une vieille bouteille couverte d'algues vient percuter le pied de {message.author.mention}...*\n"
                    f"Intrigué, il ramasse l'objet, fait sauter le bouchon et lit le parchemin anonyme à voix haute devant tout l'équipage :\n\n"
                    f"**« {bouteille_trouvee} »**\n\n"
                )
                
                await message.channel.send(intro)

async def setup(bot):
    await bot.add_cog(Bouteille(bot))