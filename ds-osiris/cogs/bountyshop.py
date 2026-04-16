import discord
import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from iaosiris import ia_osiris

SCORE_FILE = "data/scores.json"
BOUNTY_FILE = "data/bounties.json"
BOUNTY_TIMERS_FILE = "data/bounty_timers.json" # --- NOUVEAU : Fichier pour le temps ---

RANG_ROLES = {
    50: 1493542016263524412,
    150: 1493542334715924480,
    500: 1493542537712107612
}

class BountyShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seuil_chasse_base = 50
        self.en_chasse = []
        self.tempete_en_cours = False
        self.maledictions = set()
        self.bot.osiris_master_id = None
        self.bot.pacte_actif = False
        
        self.cooldowns_cibles = {}     
        self.cooldowns_chasseurs = {}  

        # --- NOUVEAU : Lance la vérification des primes périmées ---
        self.expire_bounties.start()

    def cog_unload(self):
        self.expire_bounties.cancel()

    def load_json(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def reset_timer(self, cid):
        timers = self.load_json(BOUNTY_TIMERS_FILE)
        timers[str(cid)] = datetime.now().timestamp() + 86400
        self.save_json(BOUNTY_TIMERS_FILE, timers)

    @tasks.loop(minutes=30)
    async def expire_bounties(self):
        timers = self.load_json(BOUNTY_TIMERS_FILE)
        bounties = self.load_json(BOUNTY_FILE)
        now = datetime.now().timestamp()
        changed = False

        for cid, expire_time in list(timers.items()):
            if now > expire_time:
                if bounties.get(cid, 0) > 0:
                    bounties[cid] = 0
                    changed = True
                    
                    for guild in self.bot.guilds:
                        member = guild.get_member(int(cid))
                        if member:
                            try:
                                await self.update_roles(member, 0)
                            except: pass
                            
                del timers[cid]
                changed = True

        if changed:
            self.save_json(BOUNTY_FILE, bounties)
            self.save_json(BOUNTY_TIMERS_FILE, timers)

    @expire_bounties.before_loop
    async def before_expire_bounties(self):
        await self.bot.wait_until_ready()

    async def update_roles(self, member, prime):
        try:
            roles_a_ajouter = []
            roles_a_retirer = []
            
            palier_actuel_id = None
            for seuil in sorted(RANG_ROLES.keys(), reverse=True):
                if prime >= seuil:
                    palier_actuel_id = RANG_ROLES[seuil]
                    break

            for seuil, role_id in RANG_ROLES.items():
                role = member.guild.get_role(role_id)
                if not role: continue
                
                if role_id == palier_actuel_id:
                    if role not in member.roles: roles_a_ajouter.append(role)
                else:
                    if role in member.roles: roles_a_retirer.append(role)

            if roles_a_ajouter: await member.add_roles(*roles_a_ajouter)
            if roles_a_retirer: await member.remove_roles(*roles_a_retirer)
            
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"[Erreur Rôles] : {e}")

    @commands.command(name="primes")
    async def afficher_primes(self, ctx):
        bounties = self.load_json(BOUNTY_FILE)
        primes_actives = {k: v for k, v in bounties.items() if v > 0}
        
        if not primes_actives:
            return await ctx.send("📜 **Tableau des Primes**\nAucune tête n'est mise à prix. La mer est calme.")

        primes_triees = sorted(primes_actives.items(), key=lambda item: item, reverse=True)
        embed = discord.Embed(title="📜 Tableau des Primes", description="*Les primes inactives pendant 24h expirent et sont perdues.*", color=discord.Color.gold())
        
        for index, (user_id, montant) in enumerate(primes_triees, 1):
            membre = ctx.guild.get_member(int(user_id))
            nom = membre.display_name if membre else f"Pirate disparu"
            emoji = "☠️" if montant >= 500 else "⚔️" if montant >= 150 else "🗡️"
            embed.add_field(name=f"#{index} - {nom}", value=f"{emoji} **{montant} doublons**", inline=False)
            
        embed.set_footer(text=f"Seuil de traque : {self.seuil_chasse_base} doublons minimum.")
        await ctx.send(embed=embed)

    @commands.command(name="boutique")
    async def afficher_boutique(self, ctx):
        embed = discord.Embed(title="🏴‍☠️ Le Marché Noir d'Osiris", color=discord.Color.dark_red())
        embed.add_field(name="🪵 Cale (25 pts)", value="Envoie quelqu'un au cachot (Timeout) pendant 5 min.", inline=False)
        embed.add_field(name="🦜 Perroquet (35 pts)", value="Je me moquerai cruellement de la prochaine parole de ta cible.", inline=False)
        embed.add_field(name="⚫ Marque Noire (45 pts)", value="Double la prime actuelle d'un pirate.", inline=False)
        embed.add_field(name="🗺️ Carte (50 pts)", value="Lance une chasse au trésor IA sur le serveur pour gagner 75 doublons.", inline=False)
        embed.add_field(name="🏴‍☠️ Trahison (60 pts)", value="Transfère ta propre prime sur la tête d'un innocent.", inline=False)
        embed.add_field(name="📜 Grâce (70 pts)", value="Efface ta propre prime.", inline=False)
        embed.add_field(name="⛈️ Tempête (80 pts)", value="Chaos total. Renomme tout le serveur pendant 10 min.", inline=False)
        embed.add_field(name="☠️ Rhum Empoisonné (90 pts)", value="Retire 80 points (doublons) à la cible.", inline=False)
        embed.add_field(name="🏺 Pacte d'Osiris (100 pts)", value="Je deviens ton serviteur et ton protecteur pendant 1h.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="prime")
    async def mettre_prime(self, ctx, cible: discord.Member, mise: int):
        if mise <= 0 or cible.bot or cible == ctx.author: return
        scores = self.load_json(SCORE_FILE)
        auteur_id = str(ctx.author) 
        if scores.get(auteur_id, 0) < mise: return await ctx.send("Tes poches sont vides !")

        scores[auteur_id] -= mise
        self.save_json(SCORE_FILE, scores)
        
        bounties = self.load_json(BOUNTY_FILE)
        cid = str(cible.id)
        bounties[cid] = bounties.get(cid, 0) + mise
        self.save_json(BOUNTY_FILE, bounties)
        
        self.reset_timer(cid) # --- On met à jour le chrono ---

        await self.update_roles(cible, bounties[cid])
        await ctx.send(f"💰 **MISE À PRIX !** {ctx.author.display_name} ajoute {mise} doublons sur {cible.mention}.")

    @commands.command(name="chasse")
    async def lancer_chasse(self, ctx, cible: discord.Member):
        if 0 <= datetime.now().hour < 6:
            return await ctx.send("⚓ **Osiris dort.** Les traques sont interdites entre minuit et 6h du matin.")

        maintenant = datetime.now()
        
        if ctx.author.id in self.cooldowns_chasseurs:
            if maintenant < self.cooldowns_chasseurs[ctx.author.id]:
                temps_restant = (self.cooldowns_chasseurs[ctx.author.id] - maintenant).seconds // 60
                return await ctx.send(f"⚓ Repose-toi, chasseur ! Ton navire doit s'approvisionner pendant encore {temps_restant + 1} minutes.")
                
        if cible.id in self.cooldowns_cibles:
            if maintenant < self.cooldowns_cibles[cible.id]:
                temps_restant = (self.cooldowns_cibles[cible.id] - maintenant).seconds // 60
                return await ctx.send(f"🌫️ {cible.display_name} s'est fondu dans la brume. Introuvable pour encore {temps_restant + 1} minutes !")

        bounties = self.load_json(BOUNTY_FILE)
        cid = str(cible.id)
        prime = bounties.get(cid, 0)

        if prime < self.seuil_chasse_base:
            return await ctx.send(f"La prime est trop basse ({prime}). Minimum {self.seuil_chasse_base} !")
        if cible.id in self.en_chasse or getattr(self.bot, 'osiris_master_id', None) == cible.id:
            return await ctx.send("Cible protégée ou déjà traquée !")

        self.cooldowns_chasseurs[ctx.author.id] = maintenant + timedelta(minutes=10)
        self.cooldowns_cibles[cible.id] = maintenant + timedelta(minutes=15)

        self.en_chasse.append(cible.id)
        phrases_fuite = ["par là qu'ils sont passés", "que le diable m'emporte", "hisso hé", "à l'abordage", "pas de quartier"]
        phrase_survie = random.choice(phrases_fuite)

        reduction_temps = ((prime - self.seuil_chasse_base) // 20) * 15
        temps_final = max(60, 420 - reduction_temps)

        await ctx.send(f"🚨 **TRAQUE OUVERTE SUR {cible.mention} !**\n💰 Prime : **{prime}**\n⏱️ Temps pour fuir : **{temps_final}s**\nPour survivre, crie EXACTEMENT : '**{phrase_survie.upper()}**'")

        def check(m): 
            return m.author.id == cible.id and m.content.lower().strip() == phrase_survie.lower()

        try:
            await self.bot.wait_for('message', timeout=float(temps_final), check=check)
            self.en_chasse.remove(cible.id)
            
            augmentation_brute = int(bounties[cid] * 0.10)
            bonus_survie = max(10, min(augmentation_brute, 75))
            bounties[cid] += bonus_survie
            
            self.save_json(BOUNTY_FILE, bounties)
            self.reset_timer(cid) # --- Survivre remet le timer de la prime à 24h ---
            
            await self.update_roles(cible, bounties[cid])
            await ctx.send(f"💨 {cible.mention} s'est échappé ! Sa prime grimpe de {bonus_survie} et atteint **{bounties[cid]}** !")
            
        except asyncio.TimeoutError:
            if cible.id in self.en_chasse:
                self.en_chasse.remove(cible.id)
            scores = self.load_json(SCORE_FILE)
            scores[str(ctx.author)] = scores.get(str(ctx.author), 0) + prime
            bounties[cid] = 0
            
            timers = self.load_json(BOUNTY_TIMERS_FILE)
            if cid in timers:
                del timers[cid]
                self.save_json(BOUNTY_TIMERS_FILE, timers)
                
            self.save_json(SCORE_FILE, scores)
            self.save_json(BOUNTY_FILE, bounties)
            await self.update_roles(cible, 0)
            await ctx.send(f"💰 **CAPTURE !** {ctx.author.mention} encaisse les **{prime}** doublons de {cible.display_name} !")

    @commands.command(name="acheter")
    async def acheter(self, ctx, pouvoir: str, cible: discord.Member = None):
        uid = str(ctx.author)
        scores = self.load_json(SCORE_FILE)
        solde = scores.get(uid, 0)
        p = pouvoir.lower()
        
        prix = {"cale": 25, "perroquet": 35, "marque": 45, "carte": 50, "trahison": 60, "grace": 70, "tempete": 80, "tempête": 80, "rhum": 90, "pacte": 100}
        
        if p not in prix: return await ctx.send("Cet article n'existe pas.")
        if solde < prix[p]: return await ctx.send(f"Tes poches sont vides ! Il te faut {prix[p]} doublons.")

        if p in ["cale", "perroquet", "marque", "trahison", "rhum"]:
            if not cible: return await ctx.send("Il me faut une cible !")
            if cible == ctx.author: return await ctx.send("Tu ne peux pas te cibler toi-même !")
            if cible.bot: return await ctx.send("Laisse les machines tranquilles.")

        if p == "carte":
            treasure_cog = self.bot.get_cog("TreasureHunt")
            if treasure_cog and ctx.author.id in treasure_cog.chasses_actives:
                return await ctx.send("Tu as déjà une carte en main ! Termine ta chasse actuelle avant d'en racheter une.")
                
        if p == "grace" and ctx.author.id in self.en_chasse:
            return await ctx.send("⚔️ **Trop tard pour les pots-de-vin !** Tu es déjà traqué, fuis ou meurs comme un vrai pirate !")

        scores[uid] -= prix[p]
        self.save_json(SCORE_FILE, scores)
        bounties = self.load_json(BOUNTY_FILE)
        cid = str(cible.id) if cible else None

        if p == "cale":
            try:
                await cible.timeout(timedelta(minutes=5), reason="Jeté à la cale")
                await ctx.send(f"🪵 **AU CACHOT !** Osiris jette {cible.mention} dans la cale pour 5 minutes.")
            except discord.Forbidden:
                scores[uid] += prix[p]
                self.save_json(SCORE_FILE, scores)
                await ctx.send("❌ Permissions insuffisantes. Je te rends tes doublons.")

        elif p == "perroquet":
            self.maledictions.add(cible.id)
            await ctx.send(f"🦜 La **Malédiction du Perroquet** est placée sur {cible.mention}.")

        elif p == "marque":
            bounties[cid] = max(50, bounties.get(cid, 0) * 2)
            self.save_json(BOUNTY_FILE, bounties)
            self.reset_timer(cid)
            await self.update_roles(cible, bounties[cid])
            await ctx.send(f"⚫ **MARQUE NOIRE !** La prime de {cible.mention} a doublé. Elle est de **{bounties[cid]} doublons** !")
            
        elif p == "carte":
            await ctx.invoke(self.bot.get_command('chasse_tresor'))

        elif p == "trahison":
            ma_prime = bounties.get(str(ctx.author.id), 0)
            if ma_prime == 0:
                scores[uid] += prix[p]
                self.save_json(SCORE_FILE, scores)
                return await ctx.send("Tu n'as aucune prime à transférer ! Je te rends tes sous.")
            
            bounties[cid] = bounties.get(cid, 0) + ma_prime
            bounties[str(ctx.author.id)] = 0
            self.save_json(BOUNTY_FILE, bounties)
            
            timers = self.load_json(BOUNTY_TIMERS_FILE)
            if str(ctx.author.id) in timers: del timers[str(ctx.author.id)]
            timers[cid] = datetime.now().timestamp() + 86400
            self.save_json(BOUNTY_TIMERS_FILE, timers)
            
            await self.update_roles(ctx.author, 0)
            await self.update_roles(cible, bounties[cid])
            await ctx.send(f"🏴‍☠️ **TRAHISON !** {ctx.author.mention} a transféré son avis de recherche à {cible.mention} !")

        elif p == "grace":
            bounties[str(ctx.author.id)] = 0
            self.save_json(BOUNTY_FILE, bounties)
            
            timers = self.load_json(BOUNTY_TIMERS_FILE)
            if str(ctx.author.id) in timers:
                del timers[str(ctx.author.id)]
                self.save_json(BOUNTY_TIMERS_FILE, timers)
                
            await self.update_roles(ctx.author, 0)
            await ctx.send(f"📜 **GRÂCE !** Le casier de {ctx.author.mention} est effacé, sa prime est à 0.")

        elif p in ["tempête", "tempete"]:
            await self.declencher_tempete(ctx)

        elif p == "rhum":
            scores[str(cible)] = max(0, scores.get(str(cible), 0) - 80)
            self.save_json(SCORE_FILE, scores)
            await ctx.send(f"☠️ {ctx.author.mention} a glissé du **Rhum Empoisonné** à {cible.mention}. Il vient de perdre 80 doublons !")

        elif p == "pacte":
            self.bot.osiris_master_id = ctx.author.id
            await ctx.send(f"🏺 **LE PACTE EST SCELLÉ.** {ctx.author.mention}, je suis votre serviteur pour 1h.")
            await asyncio.sleep(3600)
            self.bot.osiris_master_id = None
            await ctx.send("⌛ Le pacte est terminé.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        
        if message.author.id in self.maledictions and message.content.strip() != "":
            self.maledictions.remove(message.author.id)
            facon = "Tu es Osiris le pirate. Répète ou commente ce que vient de dire cet utilisateur de manière extrêmement moqueuse et rabaissante, comme un perroquet cruel."
            try:
                reponse = await ia_osiris(message.content, facon, [], 200)
                await message.reply(f"🦜 **Craa ! Craa !**\n{reponse}")
            except Exception:
                await message.reply("🦜 *Craa ! Le crétin a parlé ! Craa !*")

    async def declencher_tempete(self, ctx):
        if self.tempete_en_cours: return await ctx.send("La mer est déjà déchaînée !")
        self.tempete_en_cours = True
        archives = {}
        noms = ["Rat de Cale", "Marin d'Eau Douce", "Jambe de Bois", "Grog Renversé", "Naufragé", "Moule Avariée"]
        
        await ctx.send("⛈️ **UNE TEMPÊTE MAGIQUE FRAPPE LA CITADELLE !**")
        
        owner = ctx.guild.owner
        if owner:
            await ctx.send(f"🌊 *La tempête fait rage ! Tout l'équipage est méconnaissable... Seul le Capitaine {owner.display_name} reste de marbre face aux vagues, son chapeau cloué sur la tête !*")

        for m in ctx.guild.members:
            if not m.bot and m.top_role < ctx.guild.me.top_role and m.id != ctx.guild.owner_id:
                archives[m.id] = m.display_name
                try: await m.edit(nick=f"{random.choice(noms)} #{random.randint(10,99)}")
                except: continue
                
        await asyncio.sleep(600)
        
        for mid, nom in archives.items():
            m = ctx.guild.get_member(mid)
            if m: 
                try: await m.edit(nick=nom)
                except: continue
        self.tempete_en_cours = False
        await ctx.send("🌅 **La mer s'apaise. Les brumes se dissipent...**")

async def setup(bot):
    await bot.add_cog(BountyShop(bot))
