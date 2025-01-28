import json
from pathlib import Path

import discord

from discord.ext import commands


thankfulness_points_file = Path("thankfulness_points.json")

if not thankfulness_points_file.exists():
    with open(thankfulness_points_file, "w") as f:
        json.dump({}, f)

with open(thankfulness_points_file, "r") as f:
    thankfulness_points = json.load(f)


class Helpers(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.slash_command(name="agradecer", description="Agradece a un ayudante.")
    async def thank(self, ctx, member: discord.Member) -> None:
        if ctx.author.id == member.id:
            await ctx.send("No puedes agradecerte a ti mismo.")
            return
        if not any(role.name.startswith("Ayudante") for role in member.roles):
            await ctx.send("Solo puedes agradecer a ayudantes.")
            return
        if str(member.id) not in thankfulness_points:
            thankfulness_points[str(member.id)] = 0
        thankfulness_points[str(member.id)] += 1
        with open(thankfulness_points_file, "w") as f:
            json.dump(thankfulness_points, f)
        await ctx.send(f"{ctx.author.mention} thanked {member.mention}.")
    
    @commands.slash_command(name="sancionar", description="Sanciona a un ayudante.")
    async def punish(self, ctx, member: discord.Member) -> None:
        if ctx.author.id == member.id:
            await ctx.send("No puedes sancionarte a ti mismo.")
            return
        if not any(role.name.startswith("Representante") for role in ctx.author.roles):
            await ctx.send("Solo los representantes pueden sancionar.")
            return
        if not any(role.name.startswith("Ayudante") for role in member.roles):
            await ctx.send("Solo puedes sancionar a ayudantes.")
            return
        if str(member.id) not in thankfulness_points:
            thankfulness_points[str(member.id)] = 0
        if thankfulness_points[str(member.id)] > 0:
            thankfulness_points[str(member.id)] -= 1
        with open(thankfulness_points_file, "w") as f:
            json.dump(thankfulness_points, f)
        await ctx.send(f"{ctx.author.mention} punished {member.mention}.")

    @commands.slash_command(name="puntos", description="Muestra los puntos de agradecimiento de un ayudante.")
    async def points(self, ctx, member: discord.Member) -> None:
        if str(member.id) not in thankfulness_points:
            await ctx.send(f"{member.mention} no tiene puntos de agradecimiento.")
            return
        await ctx.send(f"{member.mention} tiene {thankfulness_points[str(member.id)]} puntos de agradecimiento.")
    
    @commands.slash_command(name="puntos-todos", description="Muestra los puntos de agradecimiento de todos los ayudantes.")
    async def all_points(self, ctx) -> None:
        if not thankfulness_points:
            await ctx.send("Aún ningún ayudante ha recibido agradecimientos.")
            return
        await ctx.send("\n".join(f"{i + 1}. <@{member_id}>: {points}" for i, (member_id, points) in enumerate(sorted(thankfulness_points.items(), key=lambda x: x[1], reverse=True))))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        if str(member.id) in thankfulness_points:
            del thankfulness_points[str(member.id)]
            with open(thankfulness_points_file, "w") as f:
                json.dump(thankfulness_points, f)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Helpers(bot))
