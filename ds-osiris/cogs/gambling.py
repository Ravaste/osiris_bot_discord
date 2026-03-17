import discord
import random
import re
from datetime import datetime
from discord.ext import commands
from role import (
    getChanceRole, getGuardianRole, getVoyageurRole, getOneRole, getKingRole,
    getIcelosRole, getMarcoRole, getAlexRole, getMenaceRole, getSaMajesteRole,
    getCoeurPurRole, getErreurRole, getPIncontrolableRole, getConteRole,
    getPirateRole, getDeserteurRole, getSecretRole, getRadieuxRole,
    getVagabondRole, getLegendeRole, getRenaissanceRole, getDernierRole,
    getPasseRole, getInquietantRole, getadminsystemeRole
)


def sauvegarde():
    with open('data/sauvegarde.txt', 'r') as file:
        content = file.readlines()
        input_str = content[-1].strip()
        pattern = re.compile(r'(\w+)\s*=\s*([^,]+)')
        matches = pattern.findall(input_str)
        return {key: int(value) for key, value in matches}


def tempo_roll(roll_origine, roll_mis_a_jour):
    with open('data/sauvegarde.txt', 'w') as file:
        file.write(', '.join(f"{key}={value}" for key, value in roll_mis_a_jour.items()))
    return roll_origine


async def nbrRoll(membre, actif=0):
    membre_roll = sauvegarde()
    if membre in membre_roll:
        membre_roll[membre] += 1
    else:
        membre_roll[membre] = 1
    new_roll = membre_roll
    membre_roll = tempo_roll(membre_roll, new_roll)
    if actif == 1:
        return str(membre_roll[membre])


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gambling(self, ctx, member: discord.Member, *, reason="Aucune raison n'a été renseigné"):
        """
        Pourquoi pas faire un casino dans notre serveur ??? Osiris gambling @mention
        """
        log = self.bot.get_channel(1123295747601870891)
        taverne = self.bot.get_channel(1342155918309199981)
        partage = self.bot.get_channel(1100478839622225940)

        victoire = round(random.uniform(0.0000001, 100), 6)
        roll_count = await nbrRoll(member.name, 1)
        skip = 0

        print(roll_count)

        if int(roll_count) % 500 == 0 and int(roll_count) not in [0, 1]:
            victoire = round(random.uniform(0.0000001, 2), 6)
            await ctx.send(f"T'es activité m'interesse, voila un cadeau de ma part {member.mention}")

        await log.send(f"{member} GAMBLING ! a {datetime.now().strftime('%H:%M')} et a drop : {victoire}%")

        if ctx.channel.id == 1249453012435603496:

            if victoire == 0.000001:
                skip = 1
                await log.send(f"MALHEUR {member} a chopper DANGER SYSTEME ! BEBEEEEEEERR ! VITE")
                gamblingRole = await getMenaceRole(ctx)
                await ctx.send("!!!!!??!!!??!")
                await taverne.send(f"CH?NCE : {victoire}% ?!!, ||({roll_count} roll)||")
                await partage.send(f"#####{member.mention}#####")
                await ctx.send("FORC?GE S!ST?ME")
                await ctx.send("ACT!V?TION DRO!T?")
                await ctx.send("!MPOS?!BLE")
                if any(role.name == "Origine du Groupe" for role in member.roles):
                    await ctx.send("BACKD??R TROUVE")
                    await ctx.send("INFILTRAT!ON")
                    await taverne.send("OS!R!S T0 BEB?? :")
                    await taverne.send("BASE COMPR?MISE ERREUR ???")
                    await taverne.send("UNE MENACE EST NEE")
                    await ctx.send(f"{member.mention} AS RECUPERER LES DROITS SUPERIEURS")
                    adminsystemeRole = await getadminsystemeRole(ctx)
                    await member.add_roles(adminsystemeRole, reason=reason)
                else:
                    await ctx.send("MENACE D?TECT?E // SYST?ME EN V?RROU?LLAGE // PROTOCOL D?FENS? ACTIV?")
                    await ctx.send("ZONE DANG?R?USE")
                    await ctx.send("SYST?ME V?RROU?LL? // MENACE ISOL?E")
                    await ctx.send("Rétablissement des paramètres de sécurité...")
                await member.add_roles(gamblingRole, reason=reason)

            if victoire > 0.00001 and victoire <= 0.0005:
                skip = 1
                gamblingRole = await getSecretRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send("Chance : ???%")
                await ctx.send("Audio Intercepté")
                await ctx.send(file=discord.File("musique/secret.mp3"))

            if victoire > 0.0001 and victoire <= 0.0005:
                skip = 1
                gamblingRole = await getVagabondRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"CHANCE : 0,0005% ! Esperons que tu ai trouvé la paix ||({roll_count} roll)||")
                await ctx.send(file=discord.File("image_gambling/vagabond.jpg"))
                await ctx.send("Traversant multiple contré, Tu as découvert multiple culture")
                await ctx.send("Tu as vu la richesse abondante des gens")
                await ctx.send("La pauvreté touché d'autre")
                await ctx.send("La beauté de la Nature aussi bien détruite que préservé")
                await ctx.send("Ainsi tu continue ta route à la recherche de la Sagesse et la Paix")
                await ctx.send(f"Te voila donc sur le chemin des *Vagabond* {member.mention}")

            if victoire < 0.001 and victoire >= 0.0001:
                skip = 1
                gamblingRole = await getDernierRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"CHANCE : 0,0001% ! Tu represente ce qu'il reste ||({roll_count} roll)||")
                await ctx.send(file=discord.File("image_gambling/dernier.png"))
                await ctx.send("Chassé et renié par l'influence mondial")
                await ctx.send("Le monde a effacé toute trace de ton Peuple et Histoire")
                await ctx.send(f"{member.mention}, Tu est *Le Dernier de L'Epoque Oublié*")

            if victoire < 0.01 and victoire >= 0.001:
                skip = 1
                gamblingRole = await getPasseRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send("リ⚍ꖎ リᒷ ᓭᔑ¦ℸ ̣ ᓵᒷ ᑑ⚍¦ ᓵᒷᓭℸ ̣ !¡ᔑᓭᓭᒷ∷ ᒲᔑ¦ᓭ ∷ ᒷリ ᒷℸ ̣ᔑ¦ℸ ̣ ꖎᔑ ᓵᔑ⚍ᓭᒷ ⟍̅ᒷ!¡⚍¦ᓭ ꖎᒷ ⟍̅ᒷʖ⚍ℸ ̣ ℸ ̣𝙹⚍ℸ ̣ !¡𝙹¦リᓭ ꖎᒷᓭ !¡ꖎ⚍ᓭ ᓵ∷⚍ᓵ¦ᔑꖎ ¦ꖎ リᒷ ∷ᒷᓭℸ ̣ᒷ !¡ꖎ⚍ᓭ ʖᒷᔑ⚍ᓵ𝙹⚍!¡ ⟍̅ᒷ ℸ ̣ᒷᒲ!¡ᓭ ᔑ ᓵᒷꖎ⚍¦ ᑑ⚍¦ ꖎ¦ℸ ̣ ᓵᔑ ᔑ∷∷ᒷℸ ̣ᒷ∷ ∷... ᔑ⚍ !¡ꖎ⚍ᓭ ⍊¦ℸ ̣ᒷ")

            if victoire >= 0.01 and victoire <= 0.1:
                skip = 1
                gamblingRole = await getConteRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"*CHANCE : 0.01% !!! Seul les plus érudits avait des indices* ||({roll_count} roll)||")
                await ctx.send(file=discord.File('image_gambling/comte_oublie.webp'))
                await ctx.send(f"*Il était une fois,*")
                await ctx.send(f"{member.mention} trouva un vieux livre caché dans une bibliothèque en ruine, oublié avec comme auteur R*")
                await ctx.send(f"*Un conte qui en le décryptant, devoile quelque choses de terrible mais la paix fut bref*")
                await ctx.send(f"*Une ombre apparait derrière lui , prend {member.mention} par le cou*")
                await ctx.send(f"Seul reste a present le livre ouvert a cette page contenant ces mots")
                await ctx.send(f"***NE FAIT PAS CONFIANCE AU FO...***")
                await ctx.send(f"Hélas ceci est un *Conte Oublié* nul ne sait qui était cette personne et a quoi servit ces plans")

            if victoire > 0.1 and victoire <= 0.2:
                skip = 1
                gamblingRole = await getChanceRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"*CHANCE : 0.1% !!! IMPOSSIBLE C'EST*")
                await ctx.send(file=discord.File('image_gambling/beber.png'))
                await ctx.send(f"Celui qui siege au sommet")
                await ctx.send("Celui qui est le plus puissant")
                await ctx.send("Cette personne n'est autre que ***BEBER*** !")
                await ctx.send(f"C'est le cas de le dire c'est une {str(gamblingRole)}. ||({roll_count} roll)||")

            if victoire > 0.2 and victoire <= 0.8:
                skip = 1
                gamblingRole = await getSaMajesteRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance: 0.5% ? Royal ! ||({roll_count} roll)||")
                await ctx.send(f"Son sang et ces actes sont aussi noble que son statut")
                await ctx.send(f"Dans la vérité comme dans le mensonge tous ne pouvait qu'affirmer ces propos")
                await ctx.send(f"Devant lui tous posèrent leurs genoux aux sol")
                await ctx.send(f"Agenouillez vous devant *Sa Majesté* {member.mention}")

            if victoire >= 1 and victoire < 1.5:
                skip = 1
                gamblingRole = await getPIncontrolableRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance: 1% ? Une nouvelle force jaillit !")
                await ctx.send(file=discord.File('image_gambling/dokkan-broly-dokkan-agl-broly.gif'))
                await ctx.send(f"Caché de tous, cette force avait vécu dans les abysses")
                await ctx.send(f"Portant en lui, un fardeau aussi puissante qu'incontrolable")
                await ctx.send(f"Exactement {datetime.now().strftime('%H')}H et {datetime.now().strftime('%M')}min cette force explose")
                await ctx.send(f"C'est l'avènement de {member.mention}, le guerrier a la *Puissance Incontrolable* !")

            if victoire >= 1.5 and victoire < 2.5:
                skip = 1
                gamblingRole = await getCoeurPurRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance: 1.75% ? Quelle beauté ! Pour plusieur choses ||({roll_count} roll)||")
                await ctx.send(file=discord.File('image_gambling/coeur_pur.webp'))
                await ctx.send(f"Née sous la bonne étoile, nul ne pouvait le nier")
                await ctx.send(f"Lui qui est si calme que ce paysage")
                await ctx.send(f"Lui pouvant monter ce nuage magique")
                await ctx.send(f"Lui ayant une bienviellance aveuglante")
                await ctx.send(f"Lui qui était aussi pur que le diamant")
                await ctx.send(f"Voici {member.mention}, l'Homme au *Coeur Pur*")

            if victoire >= 2.5 and victoire < 3.5:
                skip = 1
                gamblingRole = await getRadieuxRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance: 3.5% ? ||({roll_count} roll)||")
                await ctx.send(file=discord.File('image_gambling/avenir.webp'))
                await ctx.send(f"Un avenir si étincelant que meme la malchance fuit")
                await ctx.send(f"Toute choses entrepris fini plus que bien")
                await ctx.send(f"Un Avenir qui crée que des ennemies")
                await ctx.send(f"C'est *L'Avenir Radieux* de {member.mention}")

            if victoire >= 3.5 and victoire < 5:
                skip = 1
                gamblingRole = await getLegendeRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance: 4.5% ? ||({roll_count} roll)||")
                await ctx.send(file=discord.File('image_gambling/legende.jpeg'))
                await ctx.send(f"Tu as su prouvé ta valeur dans ces mers")
                await ctx.send(f"Tu as su agir comme un vrai Pirate")
                await ctx.send(f"Tu as su crée une Histoire des plus excellente")
                await ctx.send(f"{member.mention} BIENVENUE PARMIE LES LEGENDES DE CES MERS")

            if victoire < 5.5 and victoire >= 5:
                skip = 1
                gamblingRole = await getIcelosRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Utilisateur : {member.mention} == Droit ???")
                await ctx.send("//Activation_Protocol ***Icélos***:")
                await ctx.send("//Execution_Commande : ??? ")
                await ctx.send(">>Obtention_des_Statuts_Icélos")
                await ctx.send(">>Directives == ZG9ubmUgbCdpbmRpY2UgPz8/ICE=")
                if any(role.name == "Chasseur" for role in member.roles):
                    await ctx.send(">>Protocol_Réussi")
                    await ctx.send(">>Protocol_Expire")
                    await ctx.send(">>Echec_de_la_Chasse")
                    await ctx.send("//Directive_Annule -> Retour_Terminal")
                else:
                    await ctx.send(">>Erreur Protocol Conditions Non Reunis")

            if victoire < 6 and victoire >= 5.5:
                skip = 1
                gamblingRole = await getGuardianRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 6% ! Nan serait-ce !")
                await ctx.send(f"{member.mention} a été pris pour disciple de Babou pour défendre ses contrée, il est désormais {str(gamblingRole)} ||({roll_count} roll)||!")

            if victoire < 6.5 and victoire >= 6:
                skip = 1
                gamblingRole = await getVoyageurRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 6.5% ! Propre tres propre")
                await ctx.send(f"{member.mention} vole tel Osiris a travers les monde, nul ne peut barrer sa liberté. Son titre ? Le {str(gamblingRole)} ||({roll_count} roll)||!")

            if victoire <= 7 and victoire >= 6.5:
                skip = 1
                gamblingRole = await getOneRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 7%, Sera tu comme lui ?")
                await ctx.send(f"{member.mention} seul et seul, il pensait être l'élu alors qu'il est juste {str(gamblingRole)}, c'est Yoris ||({roll_count} roll)||!")

            if victoire < 7.5 and victoire >= 7:
                skip = 1
                gamblingRole = await getKingRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 7,5%")
                await ctx.send(f"{member.mention} au dessus de ses compaire, il evoque un sentiment bien unique a lui, il est le {str(gamblingRole)}, l'unique Enes ||({roll_count} roll)||!")

            if victoire < 8 and victoire >= 7.5:
                skip = 1
                gamblingRole = await getMarcoRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 8%")
                await ctx.send(f"{member.mention}, bien joué PD tu as obtenu {str(gamblingRole)} ||({roll_count} roll)||")

            if victoire < 8.5 and victoire >= 8:
                skip = 1
                gamblingRole = await getAlexRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 8%")
                await ctx.send(f"Quel est cette musique que j'entend?")
                await ctx.send(f"Ce sont des Tambours ?!")
                await ctx.send(f"C'est donc ça la liberté !")
                await ctx.send(f"*{gamblingRole}* ! ||({roll_count} roll)||")

            if victoire <= 10 and victoire > 8.5:
                skip = 1
                gamblingRole = await getRenaissanceRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 10% ||({roll_count} roll)||")
                await ctx.send(f"Tel un Phoenix, Tu renais de tes cendres")
                await ctx.send(f"Tu as vu le monde pendait la désolations")
                await ctx.send(f"Tu le revoie verdoyant")
                await ctx.send(f"{member.mention} est tu fière de ta *Renaissance* ?")

            if victoire <= 15 and victoire > 10:
                skip = 1
                gamblingRole = await getInquietantRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 15% ||({roll_count} roll)||")
                await ctx.send(f"Enemie de sa Majesté")
                await ctx.send(f"Ta seule présence suffit à inspiré la peur")
                await ctx.send(f"Serais-ce une Malediction ou bien une Bénédiction")
                await ctx.send(f"Mais il reste que toi {member.mention} tu possede une *Presence Inquietante*")

            if victoire < 20.5 and victoire > 15:
                skip = 1
                gamblingRole = await getErreurRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 20%, ||({roll_count} roll)||")
                await ctx.send(f"Enemie de tous, Volonté brisé, Confiance Trahi")
                await ctx.send(f"Aussi réel que cela puisse être nul ne peux le faire confiance")
                await ctx.send(f"Renié de tous, il compris une chose que ces Actes l'ont suivie jusqu'aux bout")
                await ctx.send(f"{member.mention} compris que c'etait lui *L'ERREUR* !")

            if victoire < 30 and victoire >= 20.5:
                skip = 1
                gamblingRole = await getDeserteurRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 30%, ||({roll_count} roll)||")
                await ctx.send(f"{member.mention} decida de fuir le combat qui sait peut-etre qu'il trouveras mieux ailleurs ce *Deserteur*.")

            if victoire < 40 and victoire >= 30:
                skip = 1
                gamblingRole = await getPirateRole(ctx)
                await member.add_roles(gamblingRole, reason=reason)
                await ctx.send(f"Chance : 40%, ||({roll_count} roll)||")
                await ctx.send(f"Une fois encore un bleu prend la mer")
                await ctx.send(f"Ahoy *Pirate* {member.mention} ! découvre, pille, boit et chasse donc dans ses mers agité ! Deviendras tu une Légende ?")

            if skip == 0:
                await ctx.send(f"Bien joué, tu as rien ||Get Clipped ({roll_count} roll)||")

        else:
            await ctx.send("On ne joue pas HORS DU CASINO ")

    @commands.command()
    async def roulette(self, ctx, nombre_de_joueur: int):
        """
        Choisit un nombre aleatoire entre 1 et ton nombre
        """
        gagnant = random.randint(1, nombre_de_joueur)
        await ctx.send(f"Je choisis the number {str(gagnant)}")


async def setup(bot):
    await bot.add_cog(Gambling(bot))