import base64
import subprocess
from typing import Any

import discord
from discord.ext import commands, pages

from the_math_guys_bot.ai.handle_message import HandleMessage


def latex2image(
    latex_expression: str,
    image_name: str,
) -> None:
    with open("temp.tex", "w") as f:
        f.write(latex_expression)
    subprocess.run(["latex", "-interaction=nonstopmode", "-shell-escape", "temp.tex"])
    subprocess.run(["dvipng", "-T", "tight", "-D", "300", "-o", image_name, "temp.dvi"])


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