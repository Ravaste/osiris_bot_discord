import aiohttp
import asyncio
import discord
from datetime import date, datetime, timedelta
from datetime import time as dtime
from zoneinfo import ZoneInfo
from icalendar import Calendar
from discord.ext import commands, tasks


GROUPES_ADE = {
    "TP1": {
        "id_ressource": "8074",
        "role_id": 1483866719775883314
    },
    "TP2": {
        "id_ressource": "8095",
        "role_id": 1450905831741587527
    }
}

CHANNEL_ADE_ID = 1483397822459019274

heures_envoi = [
    dtime(hour=7, minute=30, second=0, tzinfo=ZoneInfo("Europe/Paris")),
    dtime(hour=20, minute=0, second=0, tzinfo=ZoneInfo("Europe/Paris"))
]


async def obtenir_cours(id_ressource, jours_en_plus=0, nom_groupe="", date_cible=None):
    if date_cible is None:
        date_cible = date.today() + timedelta(days=jours_en_plus)

    date_str = date_cible.strftime("%Y-%m-%d")

    url = (
        f"https://ade-web-consult.univ-amu.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"
        f"?projectId=8&resources={id_ressource}&calType=ical"
        f"&firstDate={date_str}&lastDate={date_str}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as reponse:
                if reponse.status != 200:
                    return f"Impossible de récupérer l'emploi du temps pour le {nom_groupe}."
                text = await reponse.text()
    except asyncio.TimeoutError:
        return f"⏱️ Timeout : le serveur ADE ne répond pas pour {nom_groupe}."
    except Exception as e:
        return f"❌ Erreur de connexion pour {nom_groupe} : {e}"

    try:
        calendrier = Calendar.from_ical(text)
    except Exception as e:
        return f"❌ Erreur de parsing calendrier pour {nom_groupe} : {e}"

    cours_non_tries = []
    fuseau_france = ZoneInfo("Europe/Paris")

    for composant in calendrier.walk():
        if composant.name == "VEVENT":
            try:
                titre = composant.get('summary')
                lieu = composant.get('location')

                debut_brut = composant.get('dtstart').dt
                fin_brut = composant.get('dtend').dt

                if hasattr(debut_brut, 'astimezone'):
                    debut_france = debut_brut.astimezone(fuseau_france)
                    fin_france = fin_brut.astimezone(fuseau_france)
                else:
                    debut_france = debut_brut
                    fin_france = fin_brut

                cours_non_tries.append({
                    "debut_dt": debut_france,
                    "fin_dt": fin_france,
                    "titre": titre,
                    "lieu": lieu
                })
            except Exception as e:
                print(f"Erreur parsing cours : {e}")
                continue

    cours_tries = sorted(cours_non_tries, key=lambda c: c["debut_dt"])

    liste_cours = []

    for cours in cours_tries:
        try:
            if hasattr(cours["debut_dt"], 'strftime'):
                heure_debut = cours["debut_dt"].strftime("%H:%M")
                heure_fin = cours["fin_dt"].strftime("%H:%M")
            else:
                heure_debut = "Journée"
                heure_fin = "entière"

            message_cours = (
                f"*{heure_debut} - {heure_fin}* : "
                f"**{cours['titre']}** ({cours['lieu']})"
            )
            liste_cours.append(message_cours)
        except Exception as e:
            print(f"Erreur formatage cours : {e}")
            continue

    # Formatage de la date dans le titre
    jour_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    titre_date = f"{jour_semaine[date_cible.weekday()]} {date_cible.strftime('%d/%m/%Y')}"

    if jours_en_plus == 0 and date_cible == date.today():
        titre_date = f"aujourd'hui ({titre_date})"
    elif jours_en_plus == 1 and date_cible == date.today() + timedelta(days=1):
        titre_date = f"demain ({titre_date})"

    titre_message = f"**Emploi du temps du {titre_date} - {nom_groupe}**"

    if not liste_cours:
        return f"{titre_message}\nAucun cours prévu !"

    message_final = (
        f"{titre_message}\n"
        f"-----------------------------------\n"
        + "\n\n".join(liste_cours)
    )

    return message_final


class Ade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(time=heures_envoi)
    async def envoyer_emploi_du_temps(self):
        channel = self.bot.get_channel(CHANNEL_ADE_ID)
        if not channel:
            print("Channel ADE introuvable !")
            return

        try:
            heure_actuelle = datetime.now().hour
            jours_ajout = 0 if heure_actuelle < 12 else 1

            for nom_groupe, infos in GROUPES_ADE.items():
                try:
                    # Mention du rôle
                    role_mention = f"<@&{infos['role_id']}>"
                    await channel.send(f"{role_mention} 📅 Emploi du temps :")

                    message = await obtenir_cours(
                        id_ressource=infos["id_ressource"],
                        jours_en_plus=jours_ajout,
                        nom_groupe=nom_groupe
                    )
                    await channel.send(message)
                    await channel.send("############################################\n############################################")

                except Exception as e:
                    print(f"Erreur envoi ADE {nom_groupe} : {e}")
                    await channel.send(f"❌ Erreur pour {nom_groupe} : {e}")

        except Exception as e:
            print(f"Erreur task ADE : {e}")

    @envoyer_emploi_du_temps.error
    async def ade_error(self, error):
        print(f"Erreur tâche ADE : {error}")

    @commands.command(name="ade")
    async def commande_ade(self, ctx, groupe: str = None, quand: str = None):
        """
        Affiche l'emploi du temps d'un groupe.
        Exemples :
        Osiris ade TP1
        Osiris ade TP1 demain
        Osiris ade TP1 25/03/2026
        Osiris ade TP2 01/04/2026
        """
        if groupe is None:
            await ctx.send(
                "Tu dois préciser le groupe ! Exemples :\n"
                "`Osiris ade TP1` → aujourd'hui\n"
                "`Osiris ade TP1 demain` → demain\n"
                "`Osiris ade TP1 25/03/2026` → date précise"
            )
            return

        groupe = groupe.upper()

        if groupe not in GROUPES_ADE:
            await ctx.send(
                f"Groupe inconnu : `{groupe}`. "
                f"Les groupes disponibles sont : TP1, TP2."
            )
            return

        # --- Déterminer la date cible ---
        date_cible = None
        jours_en_plus = 0

        if quand is None or quand.lower() == "aujourd'hui":
            date_cible = date.today()
            jours_en_plus = 0

        elif quand.lower() == "demain":
            date_cible = date.today() + timedelta(days=1)
            jours_en_plus = 1

        else:
            # Tentative de parsing de date au format JJ/MM/AAAA
            try:
                date_cible = datetime.strptime(quand, "%d/%m/%Y").date()
                jours_en_plus = (date_cible - date.today()).days
            except ValueError:
                await ctx.send(
                    f"Format de date invalide : `{quand}`\n"
                    f"Utilise le format `JJ/MM/AAAA` (ex: `25/03/2026`)"
                )
                return

        # Vérification que la date n'est pas trop dans le passé
        if jours_en_plus < -1:
            await ctx.send(
                f"La date `{quand}` est dans le passé !"
            )
            return

        message_attente = await ctx.send(
            f"Recherche de l'emploi du temps pour le **{groupe}**..."
        )

        try:
            infos = GROUPES_ADE[groupe]
            resultat = await obtenir_cours(
                id_ressource=infos["id_ressource"],
                jours_en_plus=jours_en_plus,
                nom_groupe=groupe,
                date_cible=date_cible
            )

            await message_attente.edit(content=f"{resultat}")

        except Exception as e:
            await message_attente.edit(content=f"❌ Erreur inattendue : {e}")


async def setup(bot):
    await bot.add_cog(Ade(bot))