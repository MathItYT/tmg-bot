import datetime
import json
import os
import subprocess
from typing import Any

import discord
from discord.ext import commands, pages, tasks as discord_tasks

from the_math_guys_bot.ai.handle_message import HandleMessage, client
from the_math_guys_bot.utils.get_images_from_message import get_files_from_message


LATEX_TEMPLATE: str = """\\documentclass[preview]{{standalone}}
\\usepackage[spanish]{{babel}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{xcolor}}

\\definecolor{{bg}}{{HTML}}{{282B30}}
\\definecolor{{fg}}{{HTML}}{{EBEBEB}}

\\begin{{document}}
\\pagecolor{{bg}}
\\color{{fg}}
$\\displaystyle {expression}$
\\end{{document}}"""


tasks_file = "tasks.json"
discord_tasks_dict = {}
if not os.path.exists(tasks_file):
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({}))
with open(tasks_file, "r", encoding="utf-8") as f:
    tasks = json.load(f)


def init_tasks(bot: commands.Bot, tasks: dict[str, dict[str, Any]]) -> None:
    for task_name, task in tasks.items():
        message_to_send = task["message_to_send"]
        hour = task["hour"]
        minute = task["minute"]
        timezone = task["timezone"]
        user_id = task["user_id"]
        @discord_tasks.loop(minutes=1)
        async def task_function():
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=timezone)))
            if now.minute != minute or now.hour != hour:
                return
            channel = bot.get_channel(1045453709221568535)
            await channel.send(f"<@{user_id}> {message_to_send}")
        discord_task = task_function.start()
        discord_tasks_dict[task_name] = discord_task


def add_tasks(bot: commands.Bot, new_tasks: list[dict[str, Any]]) -> None:
    for task in new_tasks:
        print(task)
        tasks[task["task_name"]] = task
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks))
    init_tasks(bot, {task["task_name"]: task for task in new_tasks})


def edit_tasks(bot: commands.Bot, tasks_to_edit: list[dict[str, Any]]) -> None:
    for task in tasks_to_edit:
        tasks[task["task_name"]] = task
        discord_tasks_dict[task["task_name"]].cancel()
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks))
    init_tasks(bot, {task["task_name"]: task for task in tasks_to_edit})


def remove_tasks(_: commands.Bot, tasks_to_remove: list[str]) -> None:
    for task in tasks_to_remove:
        tasks.pop(task)
        discord_tasks_dict[task].cancel()
        discord_tasks_dict.pop(task)
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks))


def latex2image(
    latex_expression: str,
    image_name: str,
) -> None:
    with open("temp.tex", "w", encoding="utf-8") as f:
        f.write(LATEX_TEMPLATE.format(expression=latex_expression))
    subprocess.run(["latex", "-interaction=nonstopmode", "-shell-escape", "temp.tex"])
    subprocess.run(["dvisvgm", "temp.dvi", "-n", "-b", "min", "-c", "1,1", "-o", image_name.replace(".png", ".svg")])
    subprocess.run(["inkscape", image_name.replace(".png", ".svg"), "--export-type=png", "--export-height=300", "--export-filename", image_name])


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
            step_formula_or_code_type = step["step_formula_text_or_code_type"]
            step_formula_or_code = step["step_formula_text_or_code"]
            step_description = step["step_description"]
            file_name = f"step{current_step}.png"
            if step_formula_or_code_type == "text":
                embeds = [discord.Embed(description=step_description).add_field(name="Texto", value=step_formula_or_code, inline=False)]
                files = None
            elif step_formula_or_code_type == "formula":
                latex2image(step_formula_or_code, file_name)
                with open(file_name, "rb") as f:
                    files = [discord.File(f, filename=file_name)]
                embeds = [discord.Embed(description=step_description).set_image(url=f"attachment://{file_name}")]
            elif step_formula_or_code_type == "code":
                embeds = [discord.Embed(description=step_description).add_field(name="Código", value=step_formula_or_code, inline=False)]
                files = None
            pages_array.append(pages.Page(embeds=embeds, files=files))
        return pages_array


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user.mentioned_in(message) and message.mention_everyone is False and message.author != self.bot.user:
            reference = message.reference
            if reference is not None:
                reference_message = await message.channel.fetch_message(reference.message_id)
                created_at = reference_message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
                language_roles = [role.name for role in reference_message.author.roles if role.name in ["Español", "English"]]
                if len(language_roles) == 1:
                    languages = language_roles[0]
                elif len(language_roles) > 1:
                    languages = "Español"
                else:
                    languages = "Lenguaje no especificado"
                reference = f"{reference_message.author.name} -- {reference_message.author.mention} -- {created_at} -- {languages} => {reference_message.content}"
            else:
                reference = None
            time = message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            languages = [role.name for role in message.author.roles if role.name in ["Español", "English"]]
            if len(languages) == 1:
                languages = languages[0]
            elif len(languages) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            response = HandleMessage.handle_message(
                message.content, message.author.name, message.author.mention,
                await get_files_from_message(client, message),
                reference,
                time,
                languages,
            )
            tasks_to_add = response["tasks_to_add"]
            tasks_to_edit = response["tasks_to_edit"]
            tasks_to_remove = response["tasks_to_remove"]
            add_tasks(self.bot, tasks_to_add)
            edit_tasks(self.bot, tasks_to_edit)
            remove_tasks(self.bot, tasks_to_remove)
            steps = response["steps"]
            introduction = response["introduction"]
            if len(steps) == 0 and len(introduction) > 0:
                await message.reply(introduction)
                return
            paginator = StepsPaginator(introduction, steps)
            ctx = await self.bot.get_context(message)
            await paginator.send(ctx, target=message.channel, reference=message)
            return
        if message.author != self.bot.user:
            reference = message.reference
            if reference is not None:
                reference_message = await message.channel.fetch_message(reference.message_id)
                languages = [role.name for role in reference_message.author.roles if role.name in ["Español", "English"]]
                if len(languages) == 1:
                    languages = languages[0]
                elif len(languages) > 1:
                    languages = "Español"
                else:
                    languages = "Lenguaje no especificado"
                created_at = reference_message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
                reference_mention = f"{reference_message.author.name} -- {reference_message.author.mention} -- {created_at} -- {languages} => {reference_message.content}"
            else:
                reference_mention = None
            languages = [role.name for role in message.author.roles if role.name in ["Español", "English"]]
            if len(languages) == 1:
                languages = languages[0]
            elif len(languages) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            time = message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            HandleMessage.append_message_history(message.content, message.author.name, message.author.mention, await get_files_from_message(client, message), reference_mention, time, languages)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if after.author == self.bot.user or before.author == self.bot.user:
            return
        reference = after.reference
        if reference is not None:
            reference_message = await after.channel.fetch_message(reference.message_id)
            created_at = reference_message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            language_roles = [role.name for role in reference_message.author.roles if role.name in ["Español", "English"]]
            if len(language_roles) == 1:
                languages = language_roles[0]
            elif len(language_roles) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            reference = f"{reference_message.author.name} -- {reference_message.author.mention} -- {created_at} -- {languages} => {reference_message.content}"
        else:
            reference = None
        if self.bot.user.mentioned_in(after) and after.mention_everyone is False:
            time = after.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            languages = [role.name for role in after.author.roles if role.name in ["Español", "English"]]
            if len(languages) == 1:
                languages = languages[0]
            elif len(languages) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            response = HandleMessage.handle_edit_message(
                before.content, after.content,
                after.author.name, after.author.mention,
                await get_files_from_message(client, after),
                reference,
                time,
                languages,
            )
            tasks_to_add = response["tasks_to_add"]
            tasks_to_edit = response["tasks_to_edit"]
            tasks_to_remove = response["tasks_to_remove"]
            add_tasks(self.bot, tasks_to_add)
            edit_tasks(self.bot, tasks_to_edit)
            remove_tasks(self.bot, tasks_to_remove)
            introduction = response["introduction"]
            steps = response.get("steps", [])
            if len(steps) == 0:
                await after.reply(introduction)
                return
            paginator = StepsPaginator(introduction, steps)
            ctx = await self.bot.get_context(after)
            await paginator.send(ctx, target=after.channel, reference=after)
            return
        time = after.created_at.strftime("%d/%m/%Y;%H:%M:%S")
        languages = [role.name for role in after.author.roles if role.name in ["Español", "English"]]
        if len(languages) == 1:
            languages = languages[0]
        elif len(languages) > 1:
            languages = "Español"
        else:
            languages = "Lenguaje no especificado"
        HandleMessage.append_message_history_edit(before.content, after.content, after.author.name, after.author.mention, await get_files_from_message(client, after), reference, time, languages)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author != self.bot.user and self.bot.user.mentioned_in(message) and message.mention_everyone is False:
            reference = message.reference
            if reference is not None:
                reference_message = await message.channel.fetch_message(reference.message_id)
                created_at = reference_message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
                language_roles = [role.name for role in reference_message.author.roles if role.name in ["Español", "English"]]
                if len(language_roles) == 1:
                    languages = languages[0]
                elif len(language_roles) > 1:
                    languages = "Español"
                else:
                    languages = "Lenguaje no especificado"
                reference_mention = f"{reference_message.author.name} -- {reference_message.author.mention} -- {created_at} -- {languages} => {reference_message.content}"
            else:
                reference_mention = None
            languages = [role.name for role in message.author.roles if role.name in ["Español", "English"]]
            if len(languages) == 1:
                languages = languages[0]
            elif len(languages) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            time = message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            response = HandleMessage.handle_delete_message(message.content, message.author.name, message.author.mention, await get_files_from_message(client, message), reference_mention, time, languages)
            tasks_to_add = response["tasks_to_add"]
            tasks_to_edit = response["tasks_to_edit"]
            tasks_to_remove = response["tasks_to_remove"]
            add_tasks(self.bot, tasks_to_add)
            edit_tasks(self.bot, tasks_to_edit)
            remove_tasks(self.bot, tasks_to_remove)
            introduction = response["introduction"]
            steps = response["steps"]
            if len(steps) == 0:
                await message.reply(introduction)
                return
            paginator = StepsPaginator(introduction, steps)
            ctx = await self.bot.get_context(message)
            await paginator.send(ctx, target=message.channel, reference=message)
            return
        elif message.author != self.bot.user:
            reference = message.reference
            if reference is not None:
                reference_message = await message.channel.fetch_message(reference.message_id)
                languages = [role.name for role in reference_message.author.roles if role.name in ["Español", "English"]]
                if len(languages) == 1:
                    languages = languages[0]
                elif len(languages) > 1:
                    languages = "Español"
                else:
                    languages = "Lenguaje no especificado"
                created_at = reference_message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
                reference_mention = f"{reference_message.author.name} -- {reference_message.author.mention} -- {created_at} -- {languages} => {reference_message.content}"
            else:
                reference_mention = None
            languages = [role.name for role in message.author.roles if role.name in ["Español", "English"]]
            if len(languages) == 1:
                languages = languages[0]
            elif len(languages) > 1:
                languages = "Español"
            else:
                languages = "Lenguaje no especificado"
            time = message.created_at.strftime("%d/%m/%Y;%H:%M:%S")
            HandleMessage.append_message_history_delete(message.content, message.author.name, message.author.mention, await get_files_from_message(client, message), reference_mention, time, languages)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(activity=discord.Game(name="Demostrar hipótesis de Riemann."))
        init_tasks(self.bot, tasks)
        print(f"Logged in as {self.bot.user}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AI(bot))