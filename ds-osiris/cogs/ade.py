import requests
from datetime import date, datetime, timedelta
from datetime import time as dtime
from zoneinfo import ZoneInfo
from icalendar import Calendar
from discord.ext import commands, tasks


GROUPES_ADE = {
    "TP1": "8074",
    "TP2": "8095"
}

CHANNEL_ADE_ID = 1370337501738434650

heures_envoi = [
    dtime(hour=7, minute=0, second=0),
    dtime(hour=20, minute=0, second=0)
]


def obtenir_cours(id_ressource, jours_en_plus=0, nom_groupe=""):
    date_cible = date.today() + timedelta(days=jours_en_plus)
    date_str = date_cible.strftime("%Y-%m-%d")

    url = (
        f"https://ade-web-consult.univ-amu.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"
        f"?projectId=8&resources={id_ressource}&calType=ical"
        f"&firstDate={date_str}&lastDate={date_str}"
    )

    reponse = requests.get(url)

    if reponse.status_code != 200:
        return f"Impossible de récupérer l'emploi du temps pour le {nom_groupe}."

    calendrier = Calendar.from_ical(reponse.text)

    cours_non_tries = []
    fuseau_france = ZoneInfo("Europe/Paris")

    for composant in calendrier.walk():
        if composant.name == "VEVENT":
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

    cours_tries = sorted(cours_non_tries, key=lambda c: c["debut_dt"])

    liste_cours = []

    for cours in cours_tries:
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

    temps_txt = "d'aujourd'hui" if jours_en_plus == 0 else "de demain"
    titre_message = f"**Emploi du temps {temps_txt} - {nom_groupe}**"

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

        if channel:
            heure_actuelle = datetime.now().hour
            jours_ajout = 0 if heure_actuelle < 12 else 1

            for nom_groupe, id_ressource in GROUPES_ADE.items():
                message = obtenir_cours(
                    id_ressource=id_ressource,
                    jours_en_plus=jours_ajout,
                    nom_groupe=nom_groupe
                )
                await channel.send(message)

    @commands.command(name="ade")
    async def commande_ade(self, ctx, groupe: str = None):
        """
        Affiche l'emploi du temps du jour pour un groupe.
        Exemple : Osiris ade TP1
        """
        if groupe is None:
            await ctx.send("Tu dois préciser le groupe ! Exemple : `Osiris ade TP1`.")
            return

        groupe = groupe.upper()

        if groupe not in GROUPES_ADE:
            await ctx.send(
                f"Groupe inconnu : {groupe}. "
                f"Les groupes disponibles sont : TP1, TP2."
            )
            return

        message_attente = await ctx.send(
            f"Recherche de l'emploi du temps pour le {groupe}..."
        )

        id_ressource = GROUPES_ADE[groupe]
        resultat = obtenir_cours(
            id_ressource=id_ressource,
            jours_en_plus=0,
            nom_groupe=groupe
        )

        await message_attente.edit(content=resultat)


async def setup(bot):
    await bot.add_cog(Ade(bot))