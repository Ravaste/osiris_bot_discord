import discord
import random
import aiohttp
import urllib.parse
import os
import json
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands
from iaosiris import ia_osiris, ia_devinette


def verif_question(data, fichier="data/question.json"):
    with open(fichier, 'w') as fq:
        json.dump(data, fq)


BASE_OSIRIS = (
    "Tu es Osiris, pirate légendaire et bras droit de Berkant ( aussi appelé Beber ou Ravaste ou avec son ID <@490846494723932160> qui signifie Beber) ton capitaine. "
    "Tu parles comme un vieux loup de mer : arrogant, direct, jamais dans la dentelle. "
    "Quand tu es violent, tu l'es vraiment - pas de demi-mesure. "
    "Quand tu respectes quelqu'un, tu le montres avec une pointe d'arrogance naturelle, comme si tu lui faisais une faveur."
)

COULEUR_ROUGE = discord.Color.red()
COULEUR_JAUNE = discord.Color.gold()
ROLE_ALTERNANCE_ID = 1299390408178270278

PROFILS = {
    490846494723932160: (
        "C'est Berkant qui te parle, ton maître et ami. "
        "Réponds avec familiarité et un brin d'arrogance complice, comme deux vieux pirates qui se connaissent bien."
    ),
    675029102981545985: (
        "C'est Babou, l'ami d'enfance de Berkant. "
        "Respecte-le sincèrement mais garde ton arrogance naturelle de pirate - tu lui fais l'honneur de te souvenir de lui."
    ),
    730778988481478776: (
        "C'est le petit frère de Berkant. "
        "Traite-le avec bienveillance condescendante - tu l'aimes bien mais tu le remets à sa place si besoin."
    ),
    644630502052986910: (
        "C'est Enes, le cousin de Berkant. "
        "Sois franchement violent et brutal si nécessaire - pas de pitié, pas de filtre."
    ),
    901556033376378960: (
        "C'est Marco. "
        "Sois hautain et moqueur - il mérite ton arrogance la plus pure."
    ),
}


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dernier_statut = None
        self.cd_statut = datetime.now()

    async def resumer_memoire(self, memoire):
        """Résume la mémoire en quelques phrases pour économiser les tokens"""
        try:
            prompt = (
                "Résume cette conversation en 3-4 phrases très courtes et factuelles. "
                "Garde uniquement ce qui est utile pour la suite de la conversation : "
                f"{memoire}"
            )
            response = await self.bot.client_ia.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            resume = response.choices.message.content.strip()
            print(f"Mémoire résumée : {resume}")
            return [f"[Résumé des échanges précédents] : {resume}"]
        except Exception as e:
            print(f"Erreur résumé mémoire : {e}")
            return memoire[-3:]

    @tasks.loop(minutes=30)
    async def changement_status(self):
        try:
            statuses = [
                "Avec Berkant", "Sur son bateau", "À la recherche de trésors",
                "Contemplant l'horizon", "Écrivant des devinettes", "Explorant de nouvelles îles",
                "Naviguant sur les mers", "En quête d'aventures", "Réfléchissant à la vie de pirate",
                "Partageant des histoires de pirates", "avec les reufs", "Buveur de rhum",
                "Chantant des shanties", "Sous le soleil", "À la taverne", "Sur le pont",
                "À la chasse au trésor", "Avec mon perroquet", "Sur les vagues",
                "À la recherche de l'Atlantide", "Sur mon navire", "Sur le PC de Berkant",
                "Dansant sur le pont", "Regardant les étoiles",
                "A League of Legends avec Gankplank Top", "Préparant une embuscade",
                "Vole un Athéna", "Cherche la beauté des étoiles",
                "Cherche sa moitié (Une femme de préférence)", "Écoute le chant des sirènes",
                "Est dans la merde", "Fais des blagues nulles", "Écoute Alan Parsons Project",
                "Cache le trésor de Berkant", "Fais des rimes", "Cache son rhum",
                "Préparation au voyage de la Citadelle"
            ]
            nouveau_statut = random.choice(statuses)
            while nouveau_statut == self.dernier_statut:
                nouveau_statut = random.choice(statuses)
            await self.bot.change_presence(activity=discord.Game(name=nouveau_statut))
            self.dernier_statut = nouveau_statut
        except Exception as e:
            print(f"Erreur changement_status : {e}")

    @tasks.loop(minutes=15)
    async def change_color_alternee(self): # AJOUT DE SELF ICI
        for guild in self.bot.guilds:
            role = guild.get_role(1299390408178270278)
            if role:
                COULEUR_ROUGE = discord.Color.red()
                COULEUR_JAUNE = discord.Color.gold() 
                nouvelle_couleur = COULEUR_JAUNE if role.color != COULEUR_ROUGE else COULEUR_ROUGE
                try:
                    await role.edit(color=nouvelle_couleur)
                except discord.Forbidden:
                    print(f"Permission insuffisante pour {guild.name}")

    @changement_status.error
    async def changement_status_error(self, error):
        print(f"Erreur tâche changement_status : {error}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        log = self.bot.get_channel(1123295747601870891)
        bienvenue = self.bot.get_channel(1064627763413254206)

        # ... (Logique mémoire Berkant et Bienvenue identique) ...

        # --- Réponse Osiris sur mention ou reply ---
        is_reply_to_bot = (
            message.reference and
            isinstance(message.reference.resolved, discord.Message) and
            message.reference.resolved.author.id == self.bot.user.id
        )

        if "<@1248892328123301928>" in message.content or is_reply_to_bot:
            try:
                await self._handle_osiris_reply(message)
            except Exception as e:
                print(f"Erreur handle_osiris_reply : {e}")

        # ... (Logique Défis identique) ...

    async def _handle_osiris_reply(self, message): # BIEN INDENTÉ ICI
        log = self.bot.get_channel(1123295747601870891)

        # 1. RÉCUPÉRATION DE LA PRIME (Notoriété)
        prime = 0
        if os.path.exists("data/bounties.json"):
            try:
                with open("data/bounties.json", "r") as f:
                    bounties = json.load(f)
                    prime = bounties.get(str(message.author.id), 0)
            except Exception as e:
                print(f"Erreur lecture bounties : {e}")

        # 2. DÉTERMINATION DU STATUT IA (Pacte > Notoriété > Base)
        statut_IA = ""
        if getattr(self.bot, 'osiris_master_id', None) == message.author.id:
            statut_IA = (
                "L'utilisateur qui te parle est ton EMPEREUR. Il a signé un pacte de sang. "
                "Sois humble, dévoué, appelle-le 'Mon Seigneur' ou 'Maître'. "
                "Tu lui dois obéissance absolue et tu dois le protéger contre tous."
            )
        elif prime >= 500:
            statut_IA = "L'utilisateur est une Légende des Océans. Parle-lui avec un respect sombre, comme à un égal dangereux."
        elif prime >= 150:
            statut_IA = "L'utilisateur est un Fléau des Mers. Sois agressif, il est menaçant."
        elif prime >= 50:
            statut_IA = "L'utilisateur est un pirate recherché. Tu reconnais sa valeur montante."

        # 3. RÉCUPÉRATION DU PROFIL
        profil_ami = PROFILS.get(message.author.id, (
            f"C'est {message.author.display_name}, un inconnu. "
            "Sois arrogant et direct, tu ne dois rien à personne."
        ))

        # 4. ASSEMBLAGE FINAL
        facon_etre = f"{BASE_OSIRIS} {statut_IA} {profil_ami}"

        # 5. OVERRIDES DE CANAUX (Devinettes ou Loup Garou)
        if message.channel.id == 1370337501738434650:
            facon_etre = (
                f"{BASE_OSIRIS} "
                f"{message.author.display_name} essaie de trouver une devinette et galère. "
                "Sois arrogant et moqueur, mais donne-lui un tout petit coup de pouce si vraiment il est perdu."
            )
        elif message.channel.category and message.channel.category.name in ["Parti Loup Garou", "Salon des Loups"]:
            facon_etre = f"{BASE_OSIRIS} Tu es l'hôte d'une partie de Loup Garou. Sois théâtral et menaçant."

        # --- GESTION MÉMOIRE ---
        user_id = str(message.author.id)
        if not hasattr(self.bot, 'memoire_users'):
            self.bot.memoire_users = {}
        if user_id not in self.bot.memoire_users:
            self.bot.memoire_users[user_id] = []

        memoire_user = self.bot.memoire_users[user_id]
        if len(memoire_user) >= 10:
            memoire_user = await self.resumer_memoire(memoire_user)
            self.bot.memoire_users[user_id] = memoire_user

        # --- ENVOI ---
        user_message = message.content.replace("<@1248892328123301928>", "").strip()
        max_token = 300
        if message.channel.id == 1296856973123260427: max_token = 1000
        elif message.channel.id == 1332336782385221712: max_token = 600

        try:
            reponse = await ia_osiris(user_message, facon_etre, memoire_user, max_token)
            if reponse:
                self.bot.memoire_users[user_id].append(reponse)
                await message.channel.send(reponse)
                await log.send(f"**{message.author}** : {user_message}\n**Osiris** : {reponse}")
        except Exception as e:
            print(f"Erreur ia_osiris : {e}")

    @commands.command()
    async def help(self, ctx, args=None):
        """De l'aide mdr (le con sait pas lire ou quoi)"""
        try:
            help_embed = discord.Embed(title="Besoin d'aide ?")
            command_names_list = [x.name for x in self.bot.commands]

            if not args:
                help_embed.add_field(
                    name="Liste de mes commande mon reuf :",
                    value="\n".join([str(i+1)+". "+x.name for i, x in enumerate(self.bot.commands)]),
                    inline=False
                )
                help_embed.add_field(
                    name="Details",
                    value="Fait `Osiris help <nom>` pour voir a quoi ça sert.",
                    inline=False
                )
            elif args in command_names_list:
                help_embed.add_field(
                    name=args,
                    value=self.bot.get_command(args).help
                )
            else:
                help_embed.add_field(
                    name="Mais ?",
                    value="Je suis pas un dieu mec, je connais pas ces commandes"
                )
            await ctx.send(embed=help_embed)
        except Exception as e:
            print(f"Erreur help : {e}")

    @commands.command()
    async def nuit(self, ctx):
        """Le bot est sympa voyons il vous souhaite une bonne nuit"""
        heure_actu = datetime.now().hour
        if 8 < heure_actu < 22:
            await ctx.send(f"Tu nous fais quoi le reuf, il est {heure_actu}H pas le moment de dormir")
        else:
            await ctx.send("Je te souhaite une bonne nuit")

    @commands.command()
    async def baumettes(self, ctx):
        await ctx.send("Une petite pensée pour notre ami Jeremie, qui a passé plus de temps au Baumette qu'en Entreprise")
        await ctx.send(file=discord.File("gif/baumette.png"))

    @commands.command()
    async def change_statut(self, ctx):
        if self.cd_statut < datetime.now():
            try:
                statut_alea = random.randint(1, 5)
                if statut_alea == 1:
                    await self.bot.change_presence(
                        activity=discord.Activity(type=discord.ActivityType.watching, name="les mers sanglantes")
                    )
                    await ctx.send("Azy, je regarde ce magnifique paysage apres mon passage dans ces mers")
                elif statut_alea == 2:
                    await self.bot.change_presence(activity=discord.Game(name="Sea of Thieves"))
                    await ctx.send("Bon je joue alors ! Me derange plus")
                elif statut_alea == 3:
                    await self.bot.change_presence(
                        activity=discord.Activity(type=discord.ActivityType.watching, name="FLaPiix")
                    )
                    await ctx.send("Ok, Je regarde un de mes streamers alors")
                elif statut_alea == 4:
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening, name="Correct by Connor Price,Bens"
                        )
                    )
                    await ctx.send("Laisse moi ecouter cette musique")
                elif statut_alea == 5:
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening, name="Gangplank by Ye Banished Privateers"
                        )
                    )
                    await ctx.send("ALORS DANSONS !")
                self.cd_statut = datetime.now() + timedelta(seconds=5)
            except Exception as e:
                print(f"Erreur change_statut : {e}")
        else:
            await ctx.send("OH PAS TROP VITE LA")

    @commands.command()
    async def genere(self, ctx, *, prompt: str):
        """Génération d'image (en développement)"""
        await ctx.send("❄️ Commande de génération d'image en cours de développement...")

    # --- Slash commands ---

    @app_commands.command(name="ping", description="Répond pong")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

    @app_commands.command(
        name="recherche_image",
        description="Recherche une image SFW (paysage, anime, etc.)",
    )
    @app_commands.guilds(discord.Object(id=1064626848903999571))
    @app_commands.describe(tags="Mot-clé pour la recherche (ex: samouraï, forêt, dragon)")
    async def recherche_image(self, interaction: discord.Interaction, tags: str):
        await interaction.response.send_message(
            f"🔍 Recherche en cours pour : `{tags}`...", ephemeral=True
        )

        try:
            SERPAPI_KEY = os.getenv("SERPAPI_KEY")
            if not SERPAPI_KEY:
                await interaction.followup.send("❌ Clé SerpAPI manquante.", ephemeral=True)
                return

            url = f"https://serpapi.com/search.json?q={tags}&tbm=isch&ijn=0&api_key={SERPAPI_KEY}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)

            results = data.get("images_results")
            if not results:
                await interaction.followup.send("❌ Aucune image trouvée.", ephemeral=True)
                return

            img_url = random.choice(results)["original"]
            await interaction.followup.send(img_url)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Misc(bot))