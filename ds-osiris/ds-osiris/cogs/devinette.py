import discord
import re
import json
import difflib
import os
from discord.ext import commands, tasks
from datetime import datetime
from iaosiris import ia_osiris, ia_devinette

TIMER_FILE = "data/timers.json"


def charger_scores():
    if os.path.exists("data/scores.json"):
        try:
            with open("data/scores.json", "r") as f:
                contenu = f.read().strip()
                return json.loads(contenu) if contenu else {}
        except json.JSONDecodeError:
            return {}
    return {}


def sauvegarder_scores(scores):
    with open("data/scores.json", "w") as f:
        json.dump(scores, f, indent=2)


def verif_question(data, fichier="data/question.json"):
    with open(fichier, 'w') as fq:
        json.dump(data, fq)


def sauvegarder_timers(bot):
    """Sauvegarde l'état de la devinette pour résister aux crashs"""
    try:
        data = {
            "cd_devinette": bot.cd_devinette.isoformat(),
            "cd_devinette_point": bot.cd_devinette_point.isoformat(),
            "cd_devinette_google": bot.cd_devinette_google.isoformat(),
            "devinnette": list(bot.devinnette) if bot.devinnette else None,
            "liste_points": bot.liste_points,
            "compteur_bonne_rep": bot.compteur_bonne_rep,
            "personne_trouve": bot.personne_trouve,
            "cd_devinette_point_status": bot.cd_devinette_point_status,
            "cd_dev_google_status": bot.cd_dev_google_status,
            "devinnette_time": bot.devinnette_time,
            "chose_a_ne_pas_dire": bot.chose_a_ne_pas_dire,
        }
        with open(TIMER_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde timers : {e}")


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


class Devinette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60)
    async def verifier_heure(self):
        if not getattr(self.bot, 'devinnette', None):
            return
        if not getattr(self.bot, 'cd_devinette', None):
            return

        now = datetime.now()
        question_pour_osiris = self.bot.get_channel(1370337501738434650)

        if now >= self.bot.cd_devinette:
            self.bot.devinnette_time = False

            if self.bot.compteur_bonne_rep == 0:
                system_prompt = (
                    "Tu es Osiris l'erudit, un ancien pirate, vieil ami de Berkant. "
                    "Hélas, personne n'a trouvé la bonne reponse... "
                    f"Voici donc la reponse : {self.bot.devinnette[1]}. Quelle deception."
                )
                user_prompt = (
                    "Formule un message clair, emouvant et concis, "
                    "adapté a ton personnage. "
                    "Et donne bien la réponse de la devinette !"
                )
            else:
                noms = ", ".join(self.bot.personne_trouve)
                system_prompt = (
                    "Tu es Osiris l'erudit, un ancien pirate, vieil ami de Berkant. "
                    f"{self.bot.compteur_bonne_rep} personnes ont trouve la bonne reponse : {noms}. "
                    f"La bonne reponse etait : {self.bot.devinnette[1]}."
                )
                user_prompt = (
                    "Felicite-les chaleureusement en un message concis et encourageant, "
                    "Et donne bien la réponse de la devinette !"
                )

            try:
                reponse_dev = await ia_osiris(
                    message=user_prompt,
                    facon_etre=system_prompt,
                    memoire=[],
                    max_token=500,
                    temperement=0.7
                )
                await question_pour_osiris.send(reponse_dev)
            except Exception as e:
                print(f"Erreur envoi réponse devinette : {e}")
            finally:
                # Supprimer le fichier timers car la devinette est terminée
                if os.path.exists(TIMER_FILE):
                    os.remove(TIMER_FILE)
                self.verifier_heure.stop()

        if now >= self.bot.cd_devinette_point and self.bot.cd_devinette_point_status:
            self.bot.cd_devinette_point_status = False
            self.bot.liste_points = [4, 5, 6]
            sauvegarder_timers(self.bot)  # Sauvegarde après changement
            if self.bot.compteur_bonne_rep == 0:
                await question_pour_osiris.send(
                    "Les points de devinette sont reduits, mais vous avez désormais le droit "
                    "a l'usage d'Internet pour trouver la réponse ! mais pas d'IA !"
                )
            else:
                await question_pour_osiris.send(
                    "Point réduit pour les joueurs n'ayant pas trouvé la réponse, mais vous avez "
                    "désormais le droit a l'usage d'Internet pour trouver la réponse ! mais pas d'IA !"
                )

        if now >= self.bot.cd_devinette_google and self.bot.cd_dev_google_status:
            self.bot.cd_dev_google_status = False
            self.bot.liste_points = [1, 2, 3]
            sauvegarder_timers(self.bot)  # Sauvegarde après changement
            if self.bot.compteur_bonne_rep == 0:
                await question_pour_osiris.send(
                    "Les points de devinette sont désormais aux minimum, vous avez désormais "
                    "le libre accès a tout type de recherche pour trouver la réponse !"
                )
            else:
                await question_pour_osiris.send(
                    "Bon point au minimum pour les joueurs n'ayant pas trouvé la réponse, "
                    "vous avez désormais le libre accès a tout type de recherche pour trouver la réponse !"
                )

    @verifier_heure.error
    async def verifier_heure_error(self, error):
        print(f"Erreur tâche verifier_heure : {error}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel.id != 1370337501738434650:
            return

        if not getattr(self.bot, 'devinnette', None):
            return

        question_pour_osiris = self.bot.get_channel(1370337501738434650)

        # Mot interdit
        if self.bot.chose_a_ne_pas_dire and self.bot.chose_a_ne_pas_dire in message.content.lower():
            user_name = str(message.author)
            scores = charger_scores()
            await question_pour_osiris.send(
                f"***J'en ai asser vue {message.author.mention} !*** "
                "Réflechissez avant de parler, pour la peine -3 points"
            )
            scores[user_name] = scores.get(user_name, 0) - 3
            sauvegarder_scores(scores)
            return

        # Aide Osiris
        if "osiris aide moi" in message.content.lower():
            if datetime.now() >= self.bot.cd_devinette_google:
                try:
                    aide = await ia_osiris(
                        message=self.bot.devinnette[1],
                        facon_etre=(
                            "Voici la reponse de la devinette que tu avais posée, "
                            "donne un leger indice SANS donner la reponse. "
                            f"Voici la reponse : {self.bot.devinnette[1]} "
                            f"et comment a tu poser la questions : {self.bot.devinnette[0]}"
                        ),
                        memoire=[],
                        max_token=500,
                        temperement=0.75
                    )
                    mot_censure = "*[Information Confidentielle]*"
                    pattern = re.compile(re.escape(self.bot.devinnette[1]), re.IGNORECASE)
                    aide_censuree = pattern.sub(mot_censure, aide)
                    await question_pour_osiris.send(aide_censuree)
                except Exception as e:
                    await question_pour_osiris.send(f"❌ Erreur lors de la génération de l'aide : {e}")
            else:
                delta = self.bot.cd_devinette_google - datetime.now()
                heures = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                await question_pour_osiris.send(
                    f"Non non non je ne vais pas t'aider encore mais dans "
                    f"*{heures}H et {minutes}* je pourrais t'aider, "
                    f"sois patient {message.author.mention}"
                )
            return

        # Bonne réponse
        if self.bot.devinnette_time and self.bot.devinnette[1].lower() in message.content.lower():
            if message.author.name in self.bot.personne_trouve:
                await question_pour_osiris.send(
                    f"Hop hop hop  vole pas des points comme ça {message.author.mention}"
                )
                return

            self.bot.compteur_bonne_rep += 1
            self.bot.personne_trouve.append(message.author.name)
            scores = charger_scores()
            user_name = str(message.author)

            try:
                await message.delete()
            except Exception as e:
                print(f"Erreur suppression message : {e}")

            rang = len(self.bot.personne_trouve)

            if rang == 1:
                pts = self.bot.liste_points[2]
            elif rang == 2:
                pts = self.bot.liste_points[1]
            else:
                pts = self.bot.liste_points[0]

            scores[user_name] = scores.get(user_name, 0) + pts

            if rang == 1:
                await question_pour_osiris.send(
                    f"Bien joué {message.author.mention}. "
                    f"Tu as obtenu +{pts} points. "
                    f"Tu as désormais {scores[user_name]} points."
                )
            elif rang == 2:
                await question_pour_osiris.send(
                    f"Bien joué {message.author.mention}. "
                    f"Tu as obtenu +{pts} points. "
                    f"Tu as désormais {scores[user_name]} points."
                )
            else:
                await question_pour_osiris.send(
                    f"Bien joué {message.author.mention}. "
                    f"Mais t'es bien en retard. "
                    f"+{pts} point quand même. "
                    f"Tu as désormais {scores[user_name]} points."
                )

            sauvegarder_scores(scores)
            sauvegarder_timers(self.bot)  # Sauvegarde après bonne réponse
            return

        # Proximité réponse
        elif self.bot.devinnette_time:
            user_answer = message.content.lower()
            correct_answer = self.bot.devinnette[1].lower()
            ratio = difflib.SequenceMatcher(None, correct_answer, user_answer).ratio()
            mots_utilisateur = set(re.findall(r'\w+', user_answer))
            mots_corrects = set(re.findall(r'\w+', correct_answer))
            mots_en_commun = mots_utilisateur & mots_corrects

            if ratio > 0.8:
                await question_pour_osiris.send(
                    f"Pas tout à fait {message.author.mention}, mais t'y es presque !"
                )
            elif ratio > 0.6 or len(mots_en_commun) > 0:
                await question_pour_osiris.send(
                    f"{message.author.mention}, tu chauffes..."
                )

        elif not self.bot.devinnette_time and self.bot.devinnette[1].lower() in message.content.lower():
            await question_pour_osiris.send(
                f"{message.author.mention} et tu crois que ça va passer après la réponse ? ||fdp||"
            )

    @commands.command()
    async def scores(self, ctx):
        """Afficher le classement des devinettes d'Osiris"""
        scores = charger_scores()
        if not scores:
            await ctx.send("Aucun score enregistré pour le moment.")
            return

        classement = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        message = "**🏆 Classement :**\n"
        for i, (user, score) in enumerate(classement, 1):
            message += f"{i}. {user} — {score} point(s)\n"
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Devinette(bot))