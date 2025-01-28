import os

from dotenv import load_dotenv

import discord
from discord.ext import commands


def main() -> None:
    load_dotenv()
    bot: commands.Bot = commands.Bot(intents=discord.Intents.all())
    bot.load_extension("the_math_guys_bot.cogs.ai")
    bot.load_extension("the_math_guys_bot.cogs.helpers")
    bot.load_extension("the_math_guys_bot.cogs.inactive_kick")
    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
