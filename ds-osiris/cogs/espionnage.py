import discord
from discord.ext import commands

class Espionnage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SALON_SECRET_ID = 1495780043769647214 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.guild is None:
            
            salon_secret = self.bot.get_channel(self.SALON_SECRET_ID)
            
            if salon_secret:
                embed = discord.Embed(
                    title="👁️ Interception de Message Privé",
                    description=message.content if message.content else "*[Aucun texte]*",
                    color=discord.Color.dark_red()
                )
                
                avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                embed.set_author(name=f"{message.author.display_name} ({message.author.name})", icon_url=avatar_url)
                embed.set_footer(text=f"ID du rat : {message.author.id}")

                if message.attachments:
                    liens_fichiers = "\n".join([fichier.url for fichier in message.attachments])
                    embed.add_field(name="📎 Pièces jointes :", value=liens_fichiers, inline=False)
                    
                    if message.attachments.content_type and message.attachments.content_type.startswith("image"):
                        embed.set_image(url=message.attachments.url)

                await salon_secret.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Espionnage(bot))