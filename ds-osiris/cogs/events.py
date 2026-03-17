import discord
import asyncio
import json
from discord.ext import commands
from datetime import datetime, timedelta
from iaosiris import ia_osiris, ia_devinette


def verif_question(data, fichier="data/question.json"):
    with open(fichier, 'w') as fq:
        json.dump(data, fq)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_member_count(self, guild):
        member_count = len([m for m in guild.members if not m.bot])
        channel = guild.get_channel(1306307716343529502)
        if channel:
            await channel.edit(name=f"Membres : {member_count}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("El boto Online !")

        sync = await self.bot.tree.sync(guild=discord.Object(id=1064626848903999571))
        print(f"Slash commands synchronisés : {sync}")
        sync_glo = await self.bot.tree.sync()
        print(f"Slash commands global synchronisés : {sync_glo}")

        log = self.bot.get_channel(1123295747601870891)
        taverne = self.bot.get_channel(1342155918309199981)
        question_pour_osiris = self.bot.get_channel(1370337501738434650)

        print("Init variables...")
        self.bot.memoire = []
        self.bot.memoire_beber = []
        self.bot.devinnette = None
        self.bot.compteur_bonne_rep = 0
        self.bot.personne_trouve = []
        self.bot.defis_evoque = None
        self.bot.devinnette_time = True
        self.bot.liste_points = [7, 8, 9]
        self.bot.cd_devinette_point_status = True
        self.bot.cd_dev_google_status = True
        self.bot.chose_a_ne_pas_dire = None
        self.bot.mc_cooldown = False
        self.bot.heure_verrouille = datetime.now()
        self.bot.cd_devinette = datetime.now() + timedelta(hours=23, minutes=40)
        self.bot.cd_devinette_point = datetime.now() + timedelta(hours=1)
        self.bot.cd_devinette_google = datetime.now() + timedelta(hours=4)

        print("Lancement des tâches...")
        devinette_cog = self.bot.cogs.get("Devinette")
        if devinette_cog and not devinette_cog.verifier_heure.is_running():
            devinette_cog.verifier_heure.start()

        admin_cog = self.bot.cogs.get("Admin")
        if admin_cog and not admin_cog.check_temp.is_running():
            admin_cog.check_temp.start()

        misc_cog = self.bot.cogs.get("Misc")
        if misc_cog and not misc_cog.changement_status.is_running():
            misc_cog.changement_status.start()

        ade_cog = self.bot.cogs.get("Ade")
        if ade_cog and not ade_cog.envoyer_emploi_du_temps.is_running():
            ade_cog.envoyer_emploi_du_temps.start()

        if log:
            await log.send("Lancé et paré, prêt à naviguer")
        else:
            print("Channel log introuvable")

        await asyncio.sleep(2)

        print("Génération devinette...")
        try:
            self.bot.devinnette = await ia_devinette()
            print(f"Devinette : {self.bot.devinnette}")
        except Exception as e:
            print(f"ERREUR devinette : {e}")
            self.bot.devinnette = ("Devinette indisponible", "erreur")

        reponse_ds = self.bot.devinnette[1].lower() in self.bot.devinnette[0].lower()
        while reponse_ds:
            if log:
                await log.send("La devinette est trop facile, on en cherche une autre")
            self.bot.devinnette = await ia_devinette()
            reponse_ds = self.bot.devinnette[1].lower() in self.bot.devinnette[0].lower()

        try:
            self.bot.chose_a_ne_pas_dire = self.bot.devinnette[0].split("'")[-2]
            print(f"Chose a ne pas dire : {self.bot.chose_a_ne_pas_dire}")
        except Exception as e:
            print(f"ERREUR chose_a_ne_pas_dire : {e}")
            self.bot.chose_a_ne_pas_dire = None

        if log:
            await log.send(str(self.bot.devinnette))

        try:
            with open("data/question.json", 'r') as fd:
                data = json.load(fd)
        except Exception:
            data = {}

        if len(data) >= 3:
            data = {"0": self.bot.devinnette[0]}
            if log:
                await log.send("Le fichier question.json est plein, on le réinitialise")
        else:
            data[str(len(data))] = self.bot.devinnette[0]

        verif_question(data)

        if question_pour_osiris:
            await question_pour_osiris.send(
                "<@&1370347064851955808> \n"
                "Plusieurs règles avant tout :  \n"
                "1 - Interdit à Google ou IA c'est censé valoriser votre culture G pendant la 1H\n"
                "1.1 - Autorisation d'utiliser Internet après 1H, mais pas d'IA\n"
                "1.2 - Tu peux utiliser Google pour les réponses après 4H\n"
                "2 - Tu as le droit de parler avec d'autres personnes, amis\n"
                "3 - Un jeu de vitesse avec points variables\n"
                "3.1 - Si la réponse est donnée avant 1H : *1er* = 9 Points; *2ème* = 8 Points; *3ème* = 7 Points.\n"
                "3.2 - Si la réponse est donnée entre 1H et 4H : *1er* = 6 Points; *2ème* = 5 Points; *3ème* = 4 Points.\n"
                "3.3 - Si la réponse est donnée après 4H : *1er* = 3 Points; *2ème* = 2 Points; *3ème* = 1 Point.\n"
                "4 - Osiris est sensible à la casse donc accents, tirets ET TOUT autre caractère spécial est important\n"
                "4.1 - Une marge d'erreur va vous permettre de savoir si votre réponse est proche ou non\n"
                "5 - Il y a rarement voire jamais les mêmes questions\n"
                "Bien voilà les règles ! Bonne chance - *Beber*\n"
                "Voici la devinette : \n"
            )
            await question_pour_osiris.send(self.bot.devinnette[0])

        await asyncio.sleep(2)

        for guild in self.bot.guilds:
            await self.update_member_count(guild)

        print("Génération message taverne...")
        facon_etre = (
            "Tu te nommes Osiris et tu es un voyageur tel un pirate "
            "et tu es le bras droit de Berkant, dis bonjour aux habitants de La Citadelle "
            "et demande leur comment s'est passée leur journée (max 100 mots)"
        )
        try:
            full_reply = await ia_osiris("", facon_etre)
            print(f"Réponse taverne : {full_reply}")
        except Exception as e:
            print(f"ERREUR taverne : {e}")
            full_reply = None

        if taverne and full_reply:
            await taverne.send(full_reply)

        print("Fin on_ready, attente ntm...")
        def check(message):
            return message.content == 'ntm'

        try:
            await self.bot.wait_for('message', timeout=300.0, check=check)
            if taverne:
                await taverne.send("*Par les cheveux à M.Propre, c'est toi que je vais niquer*")
        except asyncio.TimeoutError:
            pass

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            print(f"Guilde {payload.guild_id} non trouvée.")
            return

        nom = payload.user.name
        log = self.bot.get_channel(1123295747601870891)
        goodbye_channel = self.bot.get_channel(1064628387538280519)

        facon_etre = (
            f"Tu te nomme Osiris et Tu es un voyageur telle un pirate et tu est le bras droit de Berkant, "
            f"dit au-revoir a notre ancien compagnion {nom} de facon honorable et concis (max 100 mots)"
        )

        await log.send(f"Nom de l'utilisateur : {nom}")

        full_reply = await ia_osiris("", facon_etre)
        if full_reply:
            await goodbye_channel.send(full_reply)
        else:
            await log.send("Je n'ai pas réussi à obtenir une réponse.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_member_count(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.update_member_count(member.guild)


async def setup(bot):
    await bot.add_cog(Events(bot))