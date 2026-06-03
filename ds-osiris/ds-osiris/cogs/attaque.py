import discord
from discord.ext import commands
from iaosiris import ia_osiris

class Attaque(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner() 
    async def attaque(self, ctx, membre: discord.Member, *, message: str = None):
        """Ordonne à Osiris d'envoyer un MP de pression (IA ou message personnalisé)."""
        
        if membre.bot:
            return await ctx.send("Tu veux que je m'insulte moi-même, Capitaine ? Je vaux mieux que ça.")

        msg_attente = await ctx.send(f"*Osiris acquiesce, charge son pistolet à silex et se dirige vers les quartiers de {membre.display_name}...*")

        if message is None:
            system_prompt = (
                "Tu es Osiris l'érudit, un ancien pirate arrogant, vieil ami de Berkant et gardien de La Citadelle. "
                "Le Capitaine t'a donné le feu vert pour intimider un membre de l'équipage en Message Privé."
            )
            user_prompt = (
                f"Rédige un message court, cinglant et menaçant destiné à {membre.display_name}. "
                "Fais-lui comprendre que tu as l'œil sur lui de la part du Capitaine et qu'il a intérêt à se tenir à carreau, "
                "sinon tu le jetteras aux requins."
            )

            try:
                texte_attaque = await ia_osiris(
                    message=user_prompt,
                    facon_etre=system_prompt,
                    memoire=[],
                    max_token=200,
                    temperement=0.8
                )
            except Exception as e:
                print(f"Erreur IA Attaque : {e}")
                return await msg_attente.edit(content="Mes canons sont enrayés. Mon cerveau IA ne répond pas.")
        else:
            texte_attaque = message

        try:
            await membre.send(texte_attaque)
            await msg_attente.edit(content=f"**Frappe réussie !** J'ai glissé le mot sous la porte de {membre.mention}. Il va trembler. Voici mon message :\n\n{texte_attaque}")
        except discord.Forbidden:
            # Sécurité si le membre a bloqué ses MP Discord
            await msg_attente.edit(content=f"**Échec !** Ce froussard de {membre.display_name} a verrouillé la porte de sa cabine (Messages Privés désactivés).")


    @attaque.error
    async def attaque_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Seul le Capitaine ou un Officier (Admin) a le droit de m'ordonner une telle attaque !")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il manque une cible ! Précise le pirate : `osiris attaque @pseudo [message optionnel]`")


async def setup(bot):
    await bot.add_cog(Attaque(bot))