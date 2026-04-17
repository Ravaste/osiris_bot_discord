import discord
import random
import os
import json
from discord.ext import commands

SCORES_FILE = "data/scores.json"

def charger_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r") as f:
                contenu = f.read().strip()
                return json.loads(contenu) if contenu else {}
        except json.JSONDecodeError:
            return {}
    return {}

def sauvegarder_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

class CitationView(discord.ui.View):
    def __init__(self, auteur_correct, options, message_citation):
        super().__init__(timeout=60.0) 
        self.auteur_correct = auteur_correct
        self.message_citation = message_citation
        self.joueurs_ayant_joue = set()

        for membre in options:
            btn = discord.ui.Button(
                label=membre.display_name, 
                style=discord.ButtonStyle.primary, 
                custom_id=str(membre.id)
            )
            btn.callback = self.bouton_callback
            self.add_item(btn)

    async def bouton_callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.joueurs_ayant_joue:
            return await interaction.response.send_message("🏴‍☠️ Tu as déjà tenté ta chance, tricheur !", ephemeral=True)
        
        self.joueurs_ayant_joue.add(interaction.user.id)

        if interaction.custom_id == str(self.auteur_correct.id):
            scores = charger_scores()
            user_name = str(interaction.user)
            pts_gagnes = 0
            scores[user_name] = scores.get(user_name, 0) + pts_gagnes
            sauvegarder_scores(scores)

            for child in self.children:
                child.disabled = True
                if child.custom_id == str(self.auteur_correct.id):
                    child.style = discord.ButtonStyle.success

            await interaction.response.edit_message(
                content=f"**« {self.message_citation} »**\n\nBien vu {interaction.user.mention} ! C'était bien **{self.auteur_correct.display_name}**. Tu gagnes **{pts_gagnes} points** !", 
                view=self
            )
            self.stop()
        else:
            await interaction.response.send_message(f"Raté ! Ce n'était pas lui.", ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            if child.custom_id == str(self.auteur_correct.id):
                child.style = discord.ButtonStyle.success
        
        try:
            await self.message.edit(content=f"Temps écoulé, bande de moussaillons amnésiques ! C'était **{self.auteur_correct.display_name}** qui avait dit ça.", view=self)
        except:
            pass


class Citation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jeu_en_cours = False

    @commands.command()
    async def citation(self, ctx):
        """Lance le mini-jeu : Qui a dit ça ?"""
        
        if self.jeu_en_cours:
            return await ctx.send("⏳ Du calme ! Osiris cherche déjà une citation. Finissez la partie en cours d'abord !")

        self.jeu_en_cours = True #
        try:
            msg_attente = await ctx.send("🔍 *Osiris fouille dans les archives poussiéreuses de la Taverne...*")

            messages_valides = []
            auteurs_uniques = set()

            async for msg in ctx.channel.history(limit=5000):
                if msg.author.bot:
                    continue
                
                auteurs_uniques.add(msg.author)

                if not msg.attachments and not msg.content.lower().startswith('osiris') and len(msg.content) > 3:
                    messages_valides.append(msg)

            if len(auteurs_uniques) < 4 or not messages_valides:
                self.jeu_en_cours = False 
                return await msg_attente.edit(content="Pas assez de bavards ou de messages exploitables dans ce salon pour jouer.")

            message_gagnant = random.choice(messages_valides)
            auteur_correct = message_gagnant.author

            auteurs_possibles = list(auteurs_uniques - {auteur_correct})
            if len(auteurs_possibles) > 3:
                mauvaises_reponses = random.sample(auteurs_possibles, 3)
            else:
                mauvaises_reponses = auteurs_possibles

            options = mauvaises_reponses + [auteur_correct]
            random.shuffle(options)

            view = CitationView(auteur_correct, options, message_gagnant.content)
            
            view.message = await msg_attente.edit(
                content=f"**« {message_gagnant.content} »**\n\nQui a bien pu dire une chose pareille ? Vous avez 60 secondes !", 
                view=view
            )
            
            await view.wait()
            
        finally:
            self.jeu_en_cours = False

async def setup(bot):
    await bot.add_cog(Citation(bot))