import discord

from discord.ext import commands

from the_math_guys_bot.ai.generate_diagram import GenerateDiagram
from the_math_guys_bot.ai.handle_message import HandleMessage
from the_math_guys_bot.utils.get_images_from_message import get_images_from_message


class Diagram(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="diagrama", aliases=["diagram"])
    async def diagram(self, interaction, message: str) -> None:
        await interaction.response.defer()
        HandleMessage.message_history.append({"role": "user", "content": f"Pedido de diagrama -- <@Usuario del servidor> => {message}"})
        diagram, explanation = await GenerateDiagram.generate_diagram(message)
        if diagram is None:
            await interaction.followup.send(explanation)
            HandleMessage.message_history.append({"role": "user", "content": [{"type": "text", "text": f"Diagrama -- <@Generador de diagramas> => {explanation}"}]})
            return
        ds_message = await interaction.followup.send(explanation, files=[discord.File(diagram, "diagram.png")])
        HandleMessage.message_history.append({"role": "user", "content": [{"type": "text", "text": f"Diagrama -- <@Generador de diagramas> => {explanation}"}, *({"type": "image_url", "image_url": {"url": attachment.url, "detail": "high"}} for attachment in ds_message.attachments)]})


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Diagram(bot))
