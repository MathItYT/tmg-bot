import base64
from typing import Any

import matplotlib
import matplotlib.pyplot as plt

import discord
from discord.ext import commands, pages

from the_math_guys_bot.ai.handle_message import HandleMessage


matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["text.usetex"] = True


# Credits: https://medium.com/@ealbanez/how-to-easily-convert-latex-to-images-with-python-9062184dc815
def latex2image(
    latex_expression, image_name, image_size_in=(3, 0.5), fontsize=16, dpi=200
):
    """
    A simple function to generate an image from a LaTeX language string.

    Parameters
    ----------
    latex_expression : str
        Equation in LaTeX markup language.
    image_name : str or path-like
        Full path or filename including filetype.
        Accepeted filetypes include: png, pdf, ps, eps and svg.
    image_size_in : tuple of float, optional
        Image size. Tuple which elements, in inches, are: (width_in, vertical_in).
    fontsize : float or str, optional
        Font size, that can be expressed as float or
        {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}.

    Returns
    -------
    fig : object
        Matplotlib figure object from the class: matplotlib.figure.Figure.

    """

    fig = plt.figure(figsize=image_size_in, dpi=dpi)
    text = fig.text(
        x=0.5,
        y=0.5,
        s=latex_expression,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=fontsize,
    )

    plt.savefig(image_name)

    return fig


async def get_images_from_message(message: discord.Message) -> list[str]:
    result = []
    for attachment in message.attachments:
        content_type = attachment.content_type
        if content_type.startswith("image/"):
            b64 = base64.b64encode(await attachment.read()).decode("utf-8")
            result.append(f"data:{content_type};base64,{b64}")
    if message.reference:
        reply_message = await message.channel.fetch_message(message.reference.message_id)
        result.extend(await get_images_from_message(reply_message))
    return result


class StepsPaginator(pages.Paginator):
    def __init__(self, introduction: str, steps: list[dict[str, Any]]) -> None:
        self.introduction = introduction
        self.steps = steps
        super().__init__(
            pages=self.get_pages(),
            timeout=None,
        )
    
    def get_pages(self) -> list[str]:
        pages_array = [pages.Page(content=self.introduction)]
        for current_step, step in enumerate(self.steps, start=1):
            is_formula = step["is_formula"]
            step_formula_or_code = step["step_formula_or_code"]
            step_description = step["step_description"]
            file_name = f"step{current_step}.png"
            if is_formula:
                step_formula_or_code = HandleMessage.correct_equation(step_formula_or_code)
                latex2image(step_formula_or_code, file_name)
                with open(file_name, "rb") as f:
                    files = [discord.File(f, filename=file_name)]
                embeds = [discord.Embed(description=step_description).set_image(url=f"attachment://{file_name}")]
            else:
                embeds = [discord.Embed(description=step_description).add_field(name="Código", value=HandleMessage.highlight_code(step_formula_or_code), inline=False)]
                files = None
            pages_array.append(pages.Page(embeds=embeds, files=files))
        return pages_array


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user.mentioned_in(message) and message.mention_everyone is False and message.author != self.bot.user:
            response_as_dict = HandleMessage.handle_message(
                message.content, message.author.name, message.author.mention,
                await get_images_from_message(message),
            )
            introduction = response_as_dict["introduction"]
            steps = response_as_dict["steps"]
            if len(steps) == 0:
                await message.reply(introduction)
                return
            paginator = StepsPaginator(introduction, steps)
            ctx = await self.bot.get_context(message)
            await paginator.send(ctx, target=message.channel, reference=message)
            return
        if message.author != self.bot.user:
            HandleMessage.message_history.append({"role": "user", "content": [{"type": "text", "text": f"{message.author.name} -- {message.author.mention} => {message.content}"}, *({"type": "image_url", "image_url": {"url": url, "detail": "high"}} for url in await get_images_from_message(message))]})


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AI(bot))