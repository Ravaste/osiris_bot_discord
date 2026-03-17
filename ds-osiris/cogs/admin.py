import discord
import asyncio
import re
import os
import gzip
import subprocess
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from role import getMutedRole


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def rotate_log(self):
        log_bot = "log_bot/temperature.txt"
        max_taille = 5 * 1024 * 1024
        if os.path.exists(log_bot) and os.path.getsize(log_bot) > max_taille:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"temp_{timestamp}.txt.gz"
            with open(log_bot, 'rb') as f_in, gzip.open(archive_name, 'wb') as f_out:
                f_out.writelines(f_in)
            os.remove(log_bot)

    async def restart_after_delay(self, channel, script_redemarrage):
        """Attendre 1h et redémarrer le serveur."""
        await asyncio.sleep(3600)
        await channel.send("Redémarrage du serveur après refroidissement.")
        subprocess.run(["/bin/bash", script_redemarrage])
        self.bot.mc_cooldown = False

    @tasks.loop(minutes=1)
    async def check_temp(self):
        seuil = 80
        log_bot = "log_bot/temperature.txt"
        script_arret = "/home/ravaste/minecraft/arret_serv.sh"
        script_redemarrage = "/home/ravaste/minecraft/serv_mc_screen.sh"
        channel = self.bot.get_channel(1404070367013900318)
        mc_channel = self.bot.get_channel(1403363055844462643)

        if channel is None:
            print("Channel introuvable ! Vérifie l'ID.")
            return

        def lire_temp():
            result = subprocess.run(
                ["/usr/bin/sensors"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output = result.stdout.decode()
            match = re.search(r'Package id 0:\s+\+(\d+)', output)
            if not match:
                match = re.search(r'Core 0:\s+\+(\d+)', output)
            return int(match.group(1)) if match else None

        try:
            temp = lire_temp()
            if temp is None:
                print("Température CPU non détectée dans la sortie de sensors.")
                return

            if not hasattr(self.bot, '_nbr_val_temp'):
                self.bot._nbr_val_temp = 0
                self.bot._moy_temp = 0

            self.bot._nbr_val_temp += 1
            depassement = False

            if temp >= seuil:
                mesures = []
                for _ in range(15):
                    t = lire_temp()
                    if t is not None:
                        mesures.append(t)
                    await asyncio.sleep(1)

                au_dessus = sum(1 for t in mesures if t >= seuil)
                temp = sum(mesures) / len(mesures) if mesures else 0

                if au_dessus > len(mesures) / 2:
                    depassement = True
                    await channel.send(
                        f"⚠️ Surchauffe confirmée : {temp}°C ({au_dessus}/{len(mesures)})"
                    )

            self.rotate_log()
            self.bot._moy_temp += temp

            with open(log_bot, "a") as f:
                if depassement:
                    f.write(f"ALERTE ! Température CPU du {datetime.now()} : {temp}°C\n")
                else:
                    f.write(f"Température CPU du {datetime.now()} : {temp}°C\n")

                if self.bot._nbr_val_temp >= 60:
                    self.bot._moy_temp /= self.bot._nbr_val_temp
                    if self.bot._moy_temp >= seuil:
                        await channel.send(
                            f"⚠️ Alerte : Moyenne CPU élevée : {self.bot._moy_temp:.2f}°C "
                            f"et cooldown = {self.bot.mc_cooldown}"
                        )
                        f.write(
                            f"⚠️ Alerte : Moyenne CPU élevée : {self.bot._moy_temp:.2f}°C "
                            f"et cooldown = {self.bot.mc_cooldown}\n"
                        )
                        if not self.bot.mc_cooldown:
                            self.bot.mc_cooldown = True
                            await channel.send("Le serveur va s'arrêter pour refroidissement.")
                            await mc_channel.send(
                                "Le serveur va s'arrêter pour refroidissement. "
                                "Veuillez patienter 1 heure avant de redémarrer. Merci"
                            )
                            subprocess.run(["/bin/bash", script_arret])
                            asyncio.create_task(
                                self.restart_after_delay(mc_channel, script_redemarrage)
                            )
                    else:
                        f.write(f"Moyenne des températures : {self.bot._moy_temp:.2f}°C\n")

                    f.write(f"{'-'*20} \n")
                    self.bot._nbr_val_temp = 0
                    self.bot._moy_temp = 0

        except Exception as e:
            print(f"Erreur lors de la lecture de la température : {e}")

    @commands.command()
    async def ciao(self, ctx):
        """
        #Commande Admin
        Commande pour arrêter le bot.
        """
        log = self.bot.get_channel(1123295747601870891)
        if ctx.author.id == 490846494723932160:
            await log.send("Confirmation deco")
            await ctx.send("Bonne nuit les reuf je vous dit a la prochaine !")
            await self.bot.close()
        else:
            await ctx.send("Arrache ta grand mere d'ici")

    @commands.command()
    async def bus(self, ctx, member: discord.Member, *, reason="Aucune raison n'a été renseignée"):
        """
        #Commande Admin
        LE BUS ARRIVE
        """
        if ctx.author.guild_permissions.administrator:
            mutedRole = await getMutedRole(ctx)
            await member.add_roles(mutedRole, reason=reason)
            await ctx.send(f"{member.mention} s'est mangé un bus !")
        else:
            await ctx.send("Mais tu t'est cru pour qui ?")

    @commands.command()
    async def sorti(self, ctx, member: discord.Member, *, reason="Aucune raison n'a été renseigné"):
        """
        #Commande Admin
        Frais d'hospitalisation
        """
        if ctx.author.guild_permissions.administrator:
            mutedRole = await getMutedRole(ctx)
            await member.remove_roles(mutedRole, reason=reason)
            await ctx.send(f"{member.mention} est sortie de l'hopital !")
        else:
            await ctx.send("C'est pas toi qui en a le pouvoir mdr")

    @commands.command()
    async def univers_reset(self, ctx):
        """
        #Commande Admin
        Accelere le temps pour reset Osiris.
        """
        log = self.bot.get_channel(1123295747601870891)
        if ctx.author.id == 490846494723932160:
            await log.send("Reset memoire")
            await ctx.send("Le temps ?! Il s'accelere !")
            await ctx.send(file=discord.File("gif/made-in-heaven-made-in-heaven-jojo.gif"))
            self.bot.memoire = []
            self.bot.memoire_beber = []
            await ctx.send("Berkant que c'est-il passé ?")
        else:
            await ctx.send("Que voulez-vous dire pas *Univers reset* ?")

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if guild:
            await guild.leave()
            await ctx.send(f"J'ai quitté le serveur {guild.name}")
        else:
            await ctx.send("Serveur introuvable.")

    @commands.command()
    @commands.is_owner()
    async def liste_serveurs(self, ctx):
        msg = "Serveurs où je suis présent :\n"
        for guild in self.bot.guilds:
            msg += f"- {guild.name} (ID: {guild.id})\n"
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def stop_mc(self, ctx):
        """
        #Commande Admin
        Stop le serveur mc.
        """
        self.bot.mc_cooldown = True
        script_arret = "/home/ravaste/minecraft/arret_serv.sh"
        script_redemarrage = "/home/ravaste/minecraft/serv_mc_screen.sh"

        channel = self.bot.get_channel(1404070367013900318)
        mc_channel = self.bot.get_channel(1403363055844462643)

        await channel.send("Le serveur va s'arrêter pour refroidissement.")
        await mc_channel.send(
            "Le serveur va s'arrêter pour refroidissement. "
            "Veuillez patienter 1 heure avant de redémarrer. Merci"
        )
        subprocess.run(["/bin/bash", script_arret])
        asyncio.create_task(
            self.restart_after_delay(mc_channel, script_redemarrage)
        )

@commands.command()
@commands.is_owner()
async def reload(self, ctx, cog: str):
    """Recharge un cog sans redémarrer le bot"""
    try:
        await self.bot.reload_extension(f"cogs.{cog}")
        await ctx.send(f"✅ Cog `{cog}` rechargé avec succès !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@commands.command()
@commands.is_owner()
async def load(self, ctx, cog: str):
    """Charge un nouveau cog"""
    try:
        await self.bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"✅ Cog `{cog}` chargé avec succès !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

@commands.command()
@commands.is_owner()
async def unload(self, ctx, cog: str):
    """Décharge un cog"""
    try:
        await self.bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"✅ Cog `{cog}` déchargé avec succès !")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")
        
async def setup(bot):
    await bot.add_cog(Admin(bot))