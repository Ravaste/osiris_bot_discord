import discord
import json
import os
import asyncio
from discord.ext import commands
from iaosiris import ia_osiris

SCORE_FILE = "data/scores.json"

class InsultDuels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duels_en_cours = set()

    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_scores(self, scores):
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f, indent=2)

    @commands.command(name="duel")
    async def lancer_duel(self, ctx, cible: discord.Member, mise: int):
        if mise <= 0 or cible == ctx.author or cible.bot:
            return await ctx.send("Choisis une cible valide et une mise digne de ce nom, moussaillon !")

        scores = self.load_scores()
        if scores.get(str(ctx.author), 0) < mise or scores.get(str(cible), 0) < mise:
            return await ctx.send("L'un de vous n'a pas assez de doublons pour parier !")

        if ctx.author.id in self.duels_en_cours or cible.id in self.duels_en_cours:
            return await ctx.send("Un duel est déjà en cours pour l'un d'entre vous !")

        await ctx.send(f"⚔️ {cible.mention}, {ctx.author.mention} te défie en **Duel d'Insultes** ! La mise est de **{mise} doublons**. \nTape `accepter` pour croiser les langues, ou `refuser` pour fuir comme un lâche.")

        def check_accept(m):
            return m.author == cible and m.channel == ctx.channel and m.content.lower() in ["accepter", "refuser"]

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check_accept)
            if msg.content.lower() == "refuser":
                return await ctx.send(f"🐥 {cible.display_name} s'enfuit en caquetant ! Quel manque de courage.")
        except asyncio.TimeoutError:
            return await ctx.send(f"⌛ {cible.display_name} a trop peur, il n'a même pas répondu.")

        self.duels_en_cours.add(ctx.author.id)
        self.duels_en_cours.add(cible.id)
        
        duel_log = []
        await ctx.send("⚓ **LE DUEL COMMENCE !** Préparez vos meilleures insultes de pirates.\n(Vous avez 45s chacun pour répondre)")

        async def recuperer_insulte(joueur, type_msg):
            await ctx.send(f"🎤 {joueur.mention}, envoie ton **{type_msg}** !")
            try:
                m = await self.bot.wait_for('message', timeout=45.0, check=lambda m: m.author == joueur and m.channel == ctx.channel)
                duel_log.append(f"{joueur.display_name} ({type_msg}) : {m.content}")
                return m.content
            except asyncio.TimeoutError:
                duel_log.append(f"{joueur.display_name} ({type_msg}) : [A bégayé comme une méduse]")
                await ctx.send(f"⏱️ Trop lent ! {joueur.display_name} a perdu sa langue.")
                return "[Silence]"

        # Round 1 : A insulte, B répond
        await recuperer_insulte(ctx.author, "INSULTE")
        await recuperer_insulte(cible, "RÉPARTIE")
        
        # Round 2 : B insulte, A répond
        await recuperer_insulte(cible, "INSULTE")
        await recuperer_insulte(ctx.author, "RÉPARTIE")

        await ctx.send("⚖️ **Osiris examine vos tirades...**")
        
        prompt_jugement = (
            f"Tu es Osiris, arbitre d'un duel d'insultes pirates entre {ctx.author.display_name} et {cible.display_name}. "
            f"Voici les échanges : {duel_log}. "
            "Fais ton commentaire arrogant et moqueur sur ce duel. "
            "Ensuite, tu DOIS OBLIGATOIREMENT terminer ton message par cette ligne exacte : "
            "'VAINQUEUR: [Nom du gagnant]' (choisis un des deux, ou mets AUCUN si les deux sont nuls)."
        )

        try:
            verdict = await ia_osiris("Verdict du duel", prompt_jugement, [], 400)
            await ctx.send(f"📜 **LE VERDICT D'OSIRIS :**\n{verdict}")

            nom_vainqueur = None
            lignes = verdict.split('\n')
            
            for ligne in reversed(lignes):
                if "VAINQUEUR:" in ligne.upper():
                    if ctx.author.display_name.upper() in ligne.upper():
                        nom_vainqueur = str(ctx.author)
                    elif cible.display_name.upper() in ligne.upper():
                        nom_vainqueur = str(cible)
                    break

            if nom_vainqueur:
                scores = self.load_scores()
                perdant = str(cible) if nom_vainqueur == str(ctx.author) else str(ctx.author)
                
                scores[nom_vainqueur] = scores.get(nom_vainqueur, 0) + mise
                scores[perdant] = scores.get(perdant, 0) - mise
                self.save_scores(scores)
                
                gagnant_display = ctx.author.display_name if nom_vainqueur == str(ctx.author) else cible.display_name
                await ctx.send(f"💰 {gagnant_display} remporte les **{mise} doublons** de la mise !")
            else:
                await ctx.send("🏴‍☠️ Aucun vainqueur ! Je garde les doublons pour payer mon rhum. (Match nul, personne ne gagne rien)")

        except Exception as e:
            print(f"Erreur IA : {e}")
            await ctx.send("🏴‍☠️ L'esprit d'Osiris est brouillé... L'arbitrage est impossible, gardez vos pièces.")

        finally:
            self.duels_en_cours.discard(ctx.author.id)
            self.duels_en_cours.discard(cible.id)

    @lancer_duel.error
    async def lancer_duel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("🏴‍☠️ Tu as oublié la cible ou la mise, marin d'eau douce ! Utilise : `Osiris duel @cible [mise]`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("🏴‍☠️ Je ne trouve pas ce pirate, ou ta mise n'est pas un nombre valide !")

async def setup(bot):
    await bot.add_cog(InsultDuels(bot))