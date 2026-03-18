import discord
import random
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roblox(self, ctx, genre="None"):
        """
        Choisit un jeu aleatoire avec ou sans genre compris dans :
        Horreur, Plateformer, Battleground et autre
        Si aucun genre mit la variété est total
        """
        try:
            if genre == "None":
                roblox = [
                    "Apeirophobia", "Block Tale", "Strongest Battleground", "Hero Battleground",
                    "JJK Shenanigans", "Sorcerer Battleground", "Solo showdown", "Ultimate Battleground",
                    "Space Trip", "Dungeon Quest", "Specter 2", "Abyss World",
                    "Dusty Trip", "The Mimic", "Chain", "Corridor", "Cart Ride Around Nothing"
                ]
            elif genre.lower() == "horreur":
                roblox = [
                    "Chain", "The Mimic", "The Dead", "Elmira", "Akumu",
                    "Faith", "The Tall Man", "Anomay Watch", "Specter 2", "Apeirophobia"
                ]
            elif genre.lower() == "plateformer":
                roblox = ["Steep Steps", "Abyss World"]
            elif genre.lower() == "battleground":
                roblox = [
                    "Strongest Battleground", "Hero Battleground", "JJK Shenanigans",
                    "Sorcerer Battleground", "Solo showdown", "Ultimate Battleground"
                ]
            elif genre.lower() == "autre":
                roblox = ["Blox Fruit", "Dungeon Quest", "Block Tale", "Dusty Trip", "Space Trip", "Corridor", "21"]
            elif genre.lower() == "secret":
                roblox = ["21", "Abyss World"]
            else:
                await ctx.send(f"Genre inconnu : `{genre}`. Genres disponibles : Horreur, Plateformer, Battleground, Autre, Secret")
                return

            resultat = random.choice(roblox)
            if genre == "None":
                await ctx.send(f"Voici le jeu qui est sorti : **{resultat}**")
            else:
                await ctx.send(f"Voici le jeu du style **{genre}** qui est sorti : **{resultat}**")

        except Exception as e:
            print(f"Erreur roblox : {e}")
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def nombre_premier(self, ctx, n):
        """
        2,3,5,7,13 ...
        """
        try:
            n = int(n)
            if n < 150:
                try:
                    await ctx.send(file=discord.File("gif/enricopucci-happy.gif"))
                except Exception:
                    pass
                for num in range(2, n + 1):
                    est_premier = True
                    for i in range(2, int(num**0.5) + 1):
                        if num % i == 0:
                            est_premier = False
                            break
                    if est_premier:
                        await ctx.send(num)
            else:
                await ctx.send("Calme, calme ! Tu as vraiment cru que j'allais compter plus de 150 ?")
        except ValueError:
            await ctx.send("Donne moi un nombre valide !")
        except Exception as e:
            print(f"Erreur nombre_premier : {e}")

    @commands.command()
    async def BIP(self, ctx):
        """bip bip"""
        try:
            await ctx.send(file=discord.File("gif/bipbip.mp4"))
        except Exception as e:
            print(f"Erreur BIP : {e}")
            await ctx.send("❌ Fichier BIP introuvable !")

    @commands.command()
    async def jefaisquoi(self, ctx, txt: str):
        """Ben je fais quoi ? jsp commande c'est .jefaisquoi @ texte"""
        if txt == "ADMIRE":
            await ctx.send("Trop Tard Seul Enes a passé cette étape")
        else:
            await ctx.send("Tu me dit quoi la ? Je ne comprend pas")


async def setup(bot):
    await bot.add_cog(Games(bot))