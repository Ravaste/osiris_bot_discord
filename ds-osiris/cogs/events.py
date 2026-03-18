import discord
import asyncio
import json
import os
from discord.ext import commands
from datetime import datetime, timedelta
from iaosiris import ia_osiris, ia_devinette

TIMER_FILE = "data/timers.json"


def verif_question(data, fichier="data/question.json"):
    with open(fichier, 'w') as fq:
        json.dump(data, fq)


def charger_timers():
    """Charge l'état sauvegardé si disponible"""
    if not os.path.exists(TIMER_FILE):
        return None
    try:
        with open(TIMER_FILE, 'r') as f:
            data = json.load(f)
        data["cd_devinette"] = datetime.fromisoformat(data["cd_devinette"])
        data["cd_devinette_point"] = datetime.fromisoformat(data["cd_devinette_point"])
        data["cd_devinette_google"] = datetime.fromisoformat(data["cd_devinette_google"])
        if data["devinnette"]:
            data["devinnette"] = tuple(data["devinnette"])
        return data
    except Exception as e:
        print(f"Erreur chargement timers : {e}")
        return None


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

        # --- Protection anti double on_ready ---
        if getattr(self.bot, 'already_ready', False):
            print("on_ready ignoré, bot déjà initialisé")
            return
        self.bot.already_ready = True

        sync = await self.bot.tree.sync(guild=discord.Object(id=1064626848903999571))
        print(f"Slash commands synchronisés : {sync}")
        sync_glo = await self.bot.tree.sync()
        print(f"Slash commands global synchronisés : {sync_glo}")

        log = self.bot.get_channel(1123295747601870891)
        taverne = self.bot.get_channel(1342155918309199981)
        question_pour_osiris = self.bot.get_channel(1370337501738434650)

        print("Init variables fixes...")
        self.bot.memoire = []
        self.bot.memoire_beber = []
        self.bot.defis_evoque = None
        self.bot.mc_cooldown = False
        self.bot.heure_verrouille = datetime.now()

        # --- Tentative de restauration après crash ---
        print("Vérification timers sauvegardés...")
        timers = charger_timers()

        if timers and timers["cd_devinette"] > datetime.now():
            # Crash recovery : devinette encore active
            print("♻️ Restauration après crash détectée !")
            self.bot.cd_devinette = timers["cd_devinette"]
            self.bot.cd_devinette_point = timers["cd_devinette_point"]
            self.bot.cd_devinette_google = timers["cd_devinette_google"]
            self.bot.devinnette = timers["devinnette"]
            self.bot.liste_points = timers["liste_points"]
            self.bot.compteur_bonne_rep = timers["compteur_bonne_rep"]
            self.bot.personne_trouve = timers["personne_trouve"]
            self.bot.cd_devinette_point_status = timers["cd_devinette_point_status"]
            self.bot.cd_dev_google_status = timers["cd_dev_google_status"]
            self.bot.devinnette_time = timers["devinnette_time"]
            self.bot.chose_a_ne_pas_dire = timers["chose_a_ne_pas_dire"]

            delta = self.bot.cd_devinette - datetime.now()
            heures = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            print(f"Devinette restaurée, expire dans {heures}H{minutes}min")

            if log:
                await log.send(
                    f"♻️ **Reprise après crash** — Devinette restaurée, "
                    f"expire dans **{heures}H{minutes}min**"
                )

        else:
            # Première fois ou devinette expirée : init normale
            print("Init normale devinette...")
            self.bot.devinnette = None
            self.bot.compteur_bonne_rep = 0
            self.bot.personne_trouve = []
            self.bot.devinnette_time = True
            self.bot.liste_points = [7, 8, 9]
            self.bot.cd_devinette_point_status = True
            self.bot.cd_dev_google_status = True
            self.bot.chose_a_ne_pas_dire = None
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

        # --- Génération devinette seulement si pas de restauration ---
        if not timers or timers["cd_devinette"] <= datetime.now():
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

            # Sauvegarde initiale des timers
            devinette_cog = self.bot.cogs.get("Devinette")
            if devinette_cog:
                from cogs.devinette import sauvegarder_timers
                sauvegarder_timers(self.bot)

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

        # --- Message taverne seulement si pas de restauration ---
        if not timers or timers["cd_devinette"] <= datetime.now():
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
        else:
            print("Fin on_ready (reprise crash, pas de message taverne)")

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

        try:
            await log.send(f"Nom de l'utilisateur : {nom}")
            full_reply = await ia_osiris("", facon_etre)
            if full_reply:
                await goodbye_channel.send(full_reply)
            else:
                await log.send("Je n'ai pas réussi à obtenir une réponse.")
        except Exception as e:
            print(f"Erreur on_raw_member_remove : {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_member_count(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.update_member_count(member.guild)


async def setup(bot):
    await bot.add_cog(Events(bot))