from datetime import date, timedelta
from discord.ext import commands, tasks


START_DATE_SPORT = date(2026, 1, 3)
CHANNEL_SPORT_ID = 1449851484526088416

PROG_DATA = [
    {
        "weeks": (1, 2), "tours": 3, "squats": 15, "fentes": 10,
        "pompes": "10 (genoux)", "pont": 15, "gainage": 30,
        "climbers": 20, "cardio": 30
    },
    {
        "weeks": (3, 4), "tours": 3, "squats": 16, "fentes": 11,
        "pompes": "12 (genoux)", "pont": 16, "gainage": 35,
        "climbers": 22, "cardio": 35
    },
    {
        "weeks": (5, 6), "tours": 3, "squats": 18, "fentes": 12,
        "pompes": "12-14", "pont": 18, "gainage": 40,
        "climbers": 25, "cardio": 35
    },
    {
        "weeks": (7, 8), "tours": 4, "squats": 18, "fentes": 12,
        "pompes": 14, "pont": 18, "gainage": 45,
        "climbers": "25-30", "cardio": 40
    },
    {
        "weeks": (9, 10), "tours": 4, "squats": 20, "fentes": 14,
        "pompes": 15, "pont": 20, "gainage": 50,
        "climbers": 30, "cardio": 40
    },
    {
        "weeks": (11, 12), "tours": 4, "squats": 20, "fentes": 14,
        "pompes": "15-16", "pont": 20, "gainage": 55,
        "climbers": "30-35", "cardio": "40-45"
    },
    {
        "weeks": (13, 14), "tours": 4, "squats": 22, "fentes": 16,
        "pompes": 16, "pont": 22, "gainage": 60,
        "climbers": 35, "cardio": 45
    },
    {
        "weeks": (15, 16), "tours": 4, "squats": 22, "fentes": 16,
        "pompes": "16-18", "pont": 22, "gainage": 65,
        "climbers": "35-40", "cardio": 45
    },
]


def get_current_prog():
    days_diff = (date.today() - START_DATE_SPORT).days
    week_num = (days_diff // 7) + 1

    if week_num > 16:
        return week_num, None

    for entry in PROG_DATA:
        if entry["weeks"][0] <= week_num <= entry["weeks"][1]:
            return week_num, entry

    return week_num, PROG_DATA[0]


class Sport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=30)
    async def rappel_sport_task(self):
        channel = self.bot.get_channel(CHANNEL_SPORT_ID)
        if not channel:
            print("Erreur : Salon sport introuvable")
            return

        jour_semaine = date.today().weekday()
        num_semaine, prog = get_current_prog()

        # Jours de repos (Vendredi=4, Samedi=5)
        if jour_semaine in [4, 5]:
            self.rappel_sport_task.stop()
            return

        # Programme terminé
        if not prog:
            await channel.send("🎉 **Programme de 16 semaines terminé !** Félicitations !")
            self.rappel_sport_task.stop()
            return

        intro = (
            f"🏋️ **ALERTE SPORT !** (Semaine {num_semaine})\n"
            f"C'est l'heure de bouger ton boule <@490846494723932160> !\n\n"
        )

        # Lundi (0) / Mercredi (2) : FULL BODY RENFO
        if jour_semaine in [0, 2]:
            details = (
                f"**🔥 Séance : Full Body Renfo**\n"
                f"OBJECTIF : **{prog['tours']} Tours** de ce circuit :\n"
                f"1. Squats : **{prog['squats']}**\n"
                f"2. Fentes : **{prog['fentes']}**/jambe\n"
                f"3. Pompes : **{prog['pompes']}**\n"
                f"4. Pont fessier : **{prog['pont']}**\n"
                f"5. Gainage : **{prog['gainage']} sec**\n"
                f"6. Mountain Climbers : **{prog['climbers']} reps**\n"
                f"\n*Notes: Mountain climbers lente -> rapide selon niveau.*"
            )

        # Mardi (1) / Jeudi (3) : CARDIO
        elif jour_semaine in [1, 3]:
            details = (
                f"**🏃 Séance : Cardio**\n"
                f"OBJECTIF : **{prog['cardio']} minutes**\n"
                f"- Marche rapide / Escaliers / Corde à sauter\n"
                f"- + Gainage circuit 10 min (face + côtés)\n"
                f"\n*Note: Si corde à sauter, réduire impact si genoux sensibles.*"
            )

        # Dimanche (6) : OPTIONNEL
        elif jour_semaine == 6:
            details = (
                f"**🌞 Séance : Dimanche Chill (Optionnel)**\n"
                f"- Renfo léger (2 tours max des exos renfo)\n"
                f"- OU Marche 30-40 min"
            )

        else:
            return

        await channel.send(
            intro + details +
            "\n\n*Tape `j'ai fini mon sport quotidien` pour arrêter les rappels.*"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if (
            "j'ai fini mon sport quotidien" in message.content.lower()
            and message.channel.id == CHANNEL_SPORT_ID
        ):
            self.rappel_sport_task.stop()
            await message.channel.send(
                "💪 **Bien joué !** Repose-toi bien, à demain pour la suite du programme !"
            )


async def setup(bot):
    await bot.add_cog(Sport(bot))