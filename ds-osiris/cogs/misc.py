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


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dernier_statut = None
        self.cd_statut = datetime.now()

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
                "Est dans la merde", "Fais des blagues nulles", "Écoute Alan Parson",
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

    @changement_status.error
    async def changement_status_error(self, error):
        print(f"Erreur tâche changement_status : {error}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        log = self.bot.get_channel(1123295747601870891)
        bienvenue = self.bot.get_channel(1064627763413254206)

        # --- Sauvegarde mémoire Berkant (avant tout traitement) ---
        if (
            message.author.id == 490846494723932160
            and "<@&1357765060684153034>" not in message.content
            and "<@1248892328123301928>" not in message.content
        ):
            try:
                with open("memoire/memoire_berkant.csv", 'r') as memo_berkant:
                    content = memo_berkant.read().split('$')
                    if len(content) > 10:
                        print("Memoire de Berkant trop longue, on la reset")
                        await log.send("Memoire de Berkant trop longue, on la reset")
                        with open("memoire/memoire_berkant.csv", 'w') as memo_berkant_w:
                            memo_berkant_w.write(content[-1])
                with open("memoire/memoire_berkant.csv", 'a') as memo_berkant:
                    memo_berkant.write(message.content + '$')
            except Exception as e:
                print(f"Erreur sauvegarde mémoire Berkant : {e}")

        # --- Mode Berkant ---
        if "<@&1357765060684153034>" in message.content:
            try:
                with open("memoire/memoire_berkant.csv", 'r') as memo_berkant:
                    content = memo_berkant.read().split('$')
                facon_etre = (
                    f"Tu est désormais Berkant parle comme tel voici des echantillon de comment il parle : {content}, "
                    "essaye d'imite ce style de parole, d'imiter meme les faute d'orthographe"
                )
                user_message = message.content.strip("<@1357765060684153034>").strip()
                reponse_beber = await ia_osiris(user_message, facon_etre, self.bot.memoire_beber, 1000, 0.3)
                if reponse_beber:
                    self.bot.memoire_beber.append(reponse_beber)
                    await log.send(f"{message.author} a demandé : {user_message}")
                    await log.send(f"Le bot a répondu : '{reponse_beber}'")
                    await message.channel.send(reponse_beber)
            except Exception as e:
                print(f"Erreur mode Berkant : {e}")

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

        # --- Réponses automatiques ---
        if (
            "meilleur anime" in message.content.lower()
            or "meilleur manga" in message.content.lower()
            or "meilleur fiction" in message.content.lower()
        ):
            await message.channel.send("Un des meilleurs https://fr.dragon-ball-official.com")

        # --- Bienvenue ---
        if message.channel.id == 1331659117894438974:
            try:
                user_message = message.content.strip("<@1248892328123301928>").strip()
                facon_etre = (
                    f"Tu te nomme Osiris et Tu es un voyageur telle un pirate et tu est le bras droit de Berkant, "
                    f"souhaite un bel acueil a notre nouveau moussailon {message.author}, "
                    f"(T'as premier phrase doit contenir son nom)"
                )
                role_invite = discord.utils.get(message.guild.roles, name="Invité au Serveur")
                if role_invite:
                    await message.author.add_roles(role_invite, reason="invite")
                role_citadin = discord.utils.get(message.guild.roles, name="Citadins")
                if role_citadin:
                    await message.author.add_roles(role_citadin, reason="invite")

                full_reply = await ia_osiris(user_message, facon_etre)
                if full_reply and bienvenue:
                    await bienvenue.send(message.author.mention)
                    await bienvenue.send(full_reply)
                else:
                    await log.send("Je n'ai pas réussi à obtenir une réponse. ez")
            except Exception as e:
                print(f"Erreur bienvenue : {e}")

        # --- Défis ---
        if (
            ("je participe au defi" in message.content.lower()
             or "je participe au défi" in message.content.lower())
            and "osiris" in message.content.lower()
        ):
            try:
                await message.channel.send("Bien que le défi commence alors")
                self.bot.defis_evoque = await ia_devinette()
                await log.send(str(self.bot.defis_evoque))

                try:
                    with open("data/defis.json", 'r') as fd:
                        data = json.load(fd)
                except Exception:
                    data = {}

                if len(data) >= 15:
                    data = {"0": self.bot.defis_evoque[0]}
                    print("Le fichier defis.json est plein, on le réinitialise")
                else:
                    data[str(len(data))] = self.bot.defis_evoque[0]
                verif_question(data, "data/defis.json")

                base_question = await ia_osiris(
                    message=self.bot.defis_evoque[0],
                    facon_etre=(
                        "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. "
                        "Maintenant, pose la question suivante avec un bon petit contexte, sans donner d'indice."
                    ),
                    memoire=[],
                    max_token=500,
                    temperement=0.75
                )
                await message.channel.send(f"Et bien {message.author.mention} releve cet enigme")
                await message.channel.send(base_question)
            except Exception as e:
                print(f"Erreur défi : {e}")

        if getattr(self.bot, 'defis_evoque', None) is not None:
            try:
                if self.bot.defis_evoque[1].lower() == message.content.lower():
                    reponse_defis = await ia_osiris(
                        self.bot.defis_evoque[0],
                        f"Tu est Osiris l'erudit, un ancien Pirate un vielle ami de Berkant, "
                        f"tu avais posée une question mais {message.author.name} a réussi a trouvé "
                        f"la réponse agis comme tel"
                    )
                    await message.channel.send(reponse_defis)
            except Exception as e:
                print(f"Erreur réponse défi : {e}")

    async def _handle_osiris_reply(self, message):
        log = self.bot.get_channel(1123295747601870891)

        # --- Mémoire par utilisateur ---
        user_id = str(message.author.id)
        if not hasattr(self.bot, 'memoire_users'):
            self.bot.memoire_users = {}
        if user_id not in self.bot.memoire_users:
            self.bot.memoire_users[user_id] = []

        memoire_user = self.bot.memoire_users[user_id]

        # Limite à 10 échanges par utilisateur
        if len(memoire_user) > 10:
            self.bot.memoire_users[user_id] = memoire_user[-10:]
            memoire_user = self.bot.memoire_users[user_id]

        # --- facon_etre ---
        facon_etre = (
            f"Tu te nomme Osiris et Tu es un voyageur telle un pirate et tu est le bras droit de Berkant, "
            f"réponds de manière franche, tres arrogant et SALE TRES SALE meme violent si il faut a {message.author}"
        )

        if message.author.id == 490846494723932160:
            facon_etre = "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris et tu est le bras droit de Berkant, réponds comme si c'etait Berkant qui te parlais"
            if message.channel.id == 1370337501738434650:
                facon_etre = "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. réponds comme si c'etait Berkant qui te parlais"

        if message.author.id == 675029102981545985:
            facon_etre = "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris et tu est le bras droit de Berkant, réponds de maniere respectueux car c'est l'ami d'enfance de Berkant"
            if message.channel.id == 1370337501738434650:
                facon_etre = "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. Réponds de maniere respectueux car c'est l'ami d'enfance de Berkant"

        if message.author.id == 730778988481478776:
            facon_etre = "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris et tu est le bras droit de Berkant, réponds comme si c'etait le petit frere a Berkant qui te parlais"
            if message.channel.id == 1370337501738434650:
                facon_etre = "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. réponds comme si c'etait le petit frere a Berkant qui te parlais"

        if message.author.id == 644630502052986910:
            facon_etre = "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris et tu est le bras droit de Berkant, réponds comme si c'etait le cousin (Enes) a Berkant mais de maniere franche et violente"
            if message.channel.id == 1370337501738434650:
                facon_etre = "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. réponds comme si c'etait le cousin (Enes) a Berkant mais de maniere franche et violente"

        if message.author.id == 901556033376378960:
            facon_etre = "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris et tu est le bras droit de Berkant, réponds donc a Marco de maniere arrogant"
            if message.channel.id == 1370337501738434650:
                facon_etre = "Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. réponds donc a Marco de maniere arrogant"

        if message.channel.id == 1370337501738434650:
            facon_etre = (
                f"Tu es Osiris l'erudit, un ancien Pirate, un vieil ami de Berkant. "
                f"Réponds de manière franche, tres arrogant à {message.author} "
                f"qui essaye de trouver une devinette et qui est perdu"
            )

        if message.channel.category is not None and message.channel.category.name in [
            "Parti Loup Garou", "Salon des Loups"
        ]:
            facon_etre = (
                "Tu te nomme Osiris et Tu es un voyageur telle un pirate au nom d'Osiris "
                "et tu est le bras droit de Berkant, tu est actuellement l'hote d'une "
                "parti de Loup Garou agis en tant que tel"
            )

        user_message = message.content.replace("<@1248892328123301928>", "").strip()
        max_token = 150

        if message.channel.id == 1296856973123260427:
            max_token = 1000
            await log.send(f"{message.author} a usé le channel #ultimate-osiris")

        if message.channel.id == 1332336782385221712:
            max_token = 1000

        if message.channel.category is not None and message.channel.category.name in [
            "Parti Loup Garou", "Salon des Loups"
        ]:
            max_token = 500

        try:
            reponse = await ia_osiris(user_message, facon_etre, memoire_user, max_token)
            if reponse:
                self.bot.memoire_users[user_id].append(reponse)
                await log.send(f"{message.author} a demandé : {user_message}")
                await log.send(f"Le bot a répondu : '{reponse}'")
                await message.channel.send(reponse)
            else:
                await message.channel.send("Je n'ai pas réussi à obtenir une réponse. ez")
        except Exception as e:
            print(f"Erreur ia_osiris : {e}")
            await message.channel.send("Je n'ai pas réussi à obtenir une réponse. ez")

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