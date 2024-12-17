import discord
from discord.ext import commands


class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(activity=discord.Game(name="Demostrar hipótesis de Riemann."))
        print(f"Logged in as {self.bot.user}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(OnReady(bot))
