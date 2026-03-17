import discord
import random
import asyncio
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roblox(self, ctx, genre="None"):
        """
        Choisit un jeu aleatoire avec ou sans genre compris dans :
        Horreur, Plateformer, Battleground et autre
        Si aucun genre mit la variété est total
        """
        if genre == "None":
            roblox = [
                "Apeirophobia", "Block Tale", "Strongest Battleground", "Hero Battleground",
                "JJK Shenanigans", "Sorcerer Battleground", "Solo showdown", "Ultimate Battleground",
                "Block Tale", "Space Trip", "Dungeon Quest", "Specter 2", "Abyss World",
                "Dusty Trip", "The Mimic", "Chain", "Corridor", "Cart Ride Around Nothing"
            ]
            chiffre = random.randint(0, len(roblox) - 1)
            resultat = roblox[chiffre]
            await ctx.send(f"Voici le jeu qui est sorti : {str(resultat)}")

        elif genre != "None":
            if genre.lower() == "horreur":
                roblox = [
                    "Chain", "The Mimic", "The Dead", "Elmira", "Akumu",
                    "Faith", "The Tall Man", "Anomay Watch", "Specter 2", "Apeirophobia"
                ]
            elif genre.lower() == "plateformer":
                roblox = ["Steep Steps", "Abyss World"]
            elif genre.lower() == "battleground":
                roblox = [
                    "Strongest Battleground", "Hero Battleground", "JJK Shenanigans",
                    "Sorcerer Battleground", "Solo showdown", "Ultimate Battleground"
                ]
            elif genre.lower() == "autre":
                roblox = ["Blox Fruit", "Dungeon Quest", "Block Tale", "Dusty Trip", "Space Trip", "Corridor", "21"]
            elif genre.lower() == "secret":
                roblox = ["21", "Abyss World"]
            else:
                await ctx.send(f"Genre inconnu : {genre}")
                return

            chiffre = random.randint(0, len(roblox) - 1)
            resultat = roblox[chiffre]
            await ctx.send(f"Voici le jeu du style {genre} qui est sorti : {str(resultat)}")

    @commands.command()
    async def nombre_premier(self, ctx, n):
        """
        2,3,5,7,13 ...
        """
        if int(n) < 150:
            await ctx.send(file=discord.File("gif/enricopucci-happy.gif"))
            for num in range(2, int(n) + 1):
                est_premier = True
                for i in range(2, int(num**0.5) + 1):
                    if num % i == 0:
                        est_premier = False
                        break
                if est_premier:
                    await ctx.send(num)
        else:
            await ctx.send("Calme, calme ! Tu as vraiment cru que j'allais compter plus de 150 ?")

    @commands.command()
    async def BIP(self, ctx):
        """
        bip bip
        """
        await ctx.send(file=discord.File("gif/bipbip.mp4"))

    @commands.command()
    async def jefaisquoi(self, ctx, txt: str):
        """
        Ben je fais quoi ? jsp commande c'est .jefaisquoi @ texte
        """
        if txt == "ADMIRE":
            await ctx.send("Trop Tard Seul Enes a passé cette étape")
        else:
            await ctx.send("Tu me dit quoi la ? Je ne comprend pas")

    @commands.command()
    async def loup_garou(self, ctx, nombre_loup=1):
        """
        Lancer une partie de Loup Garou
        """
        await ctx.send("Loup Garou en cours de développement...")
        return

        jour = 0
        game = True
        role_associe = {}

        guild = ctx.guild
        voice_client = ctx.author.guild.voice_client
        channel = ctx.author.voice.channel

        roles = [
            ("Sorcière", "Vous êtes la Sorcière. Pendant la nuit, vous pouvez utiliser vos potions pour tuer ou ressusciter la personne tuée."),
            ("Petite Fille", "Vous êtes la Petite Fille. Quand vous utilisez votre capacité, vous avez accès au salon des loups garous. ATTENTION, vous devez deviner un nombre pour entrer discrètement."),
            ("Chasseur", "Vous êtes le Chasseur. Lorsque vous mourrez, vous amenez quelqu'un avec vous dans la mort.")
        ]

        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        member_names_id = [(member.name, member) for member in channel.members if not member.bot]
        vivant = len(member_names_id)

        if nombre_loup > vivant // 2:
            await ctx.send("Le nombre de loups ne peut pas être plus de la moitié des joueurs.")
            return

        categorie = await guild.create_category(name="Partie Loup Garou")
        village = await guild.create_text_channel(name="village", category=categorie)

        salons_membres = {}
        for member_name, member in member_names_id:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True)
            }
            salon = await guild.create_text_channel(
                name=member_name,
                category=categorie,
                overwrites=overwrites
            )
            salons_membres[member] = salon

        liste_loup = random.sample(member_names_id, nombre_loup)
        for loup in liste_loup:
            role_associe[loup] = "Loup Garou"
            member_names_id.remove(loup)

        categorie_loup = await guild.create_category(name="Salon des Loups")

        overwrites_loup = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        for _, loup_member in liste_loup:
            overwrites_loup[loup_member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        salon_loup = await guild.create_text_channel(
            name="loups-salon",
            category=categorie_loup,
            overwrites=overwrites_loup
        )

        await salon_loup.send("Vous êtes les ***LOUPS*** déchirez leurs chairs et broyez leur OS pendant la nuit !")

        for role_name, role_desc in roles:
            if member_names_id:
                choix = random.choice(member_names_id)
                member_names_id.remove(choix)
                member_name, member = choix
                salon = salons_membres[member]
                role_associe[member] = role_name
                await salon.send(f"**Votre rôle : {role_name}**\n\n{role_desc}")

        while game:
            jour += 1

            await village.send(f"**Jour {jour}**: Tous les vivants votent pour éliminer quelqu'un.")

            embed_vote = discord.Embed(
                title="Qui voulez-vous éliminer ?",
                description="Réagissez avec l'émoticône correspondant au joueur que vous voulez éliminer.",
                color=discord.Color.blue()
            )

            reactions = []
            for index, (member_name, member) in enumerate(member_names_id):
                emoji = f"{chr(0x1F1E6 + index)}"
                embed_vote.add_field(
                    name=f"{emoji} - {member_name}",
                    value=f"Réagissez avec {emoji} pour voter.",
                    inline=False
                )
                reactions.append(emoji)

            vote_message = await village.send(embed=embed_vote)
            for emoji in reactions:
                await vote_message.add_reaction(emoji)

            votes = {emoji: 0 for emoji in reactions}

            while len(votes) < len(member_names_id):
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check=lambda r, u: r.message.id == vote_message.id and u in [m[1] for m in member_names_id]
                )
                votes[reaction.emoji] += 1

            max_votes = max(votes.values())
            eliminated_players = [emoji for emoji, vote in votes.items() if vote == max_votes]

            if len(eliminated_players) == 1:
                eliminated_emoji = eliminated_players[0]
                eliminated_member = next(
                    member[1] for member in member_names_id
                    if str(chr(0x1F1E6 + reactions.index(eliminated_emoji))) == eliminated_emoji
                )
                await village.send(f"{eliminated_member.name} a été éliminé.")
                await eliminated_member.edit(mute=True)
                await eliminated_member.add_roles(discord.utils.get(guild.roles, name="Mort"))
                member_names_id.remove((eliminated_member.name, eliminated_member))

            if len(member_names_id) <= nombre_loup:
                await ctx.send("Les loups ont gagné la partie !")
                break

            if all(member not in [loup[1] for loup in liste_loup] for member in member_names_id):
                await ctx.send("Les villageois ont gagné la partie !")
                break

            continuer_embed = discord.Embed(
                title="Souhaitez-vous continuer la partie ?",
                description="Répondez par 'oui' pour continuer ou 'non' pour arrêter la partie.",
                color=discord.Color.orange()
            )
            await village.send(embed=continuer_embed)

            def check_response(message):
                return message.author == ctx.author and message.content.lower() in ['oui', 'non']

            msg_response = await self.bot.wait_for('message', check=check_response)

            if msg_response.content.lower() == 'non':
                await ctx.send("La partie est terminée. Merci d'avoir joué !")
                game = False

        for category in [categorie, categorie_loup]:
            for ch in category.channels:
                await ch.delete()
            await category.delete()


async def setup(bot):
    await bot.add_cog(Games(bot))