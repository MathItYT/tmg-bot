import datetime
import json
from pathlib import Path
import random

import discord

from discord.ext import commands, tasks


ACTIVE_MEMBER_ROLE: int = 1327719103636574209
ACTIVITY_THRESHOLD: int = 10


class InactiveKick(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def fetch_inactive_users(self, days: int) -> None:
        active_users = []
        real_active_users = []
        guild: discord.Guild = self.bot.get_guild(1045453708642758657)
        roles = guild.roles
        role = discord.utils.get(roles, id=ACTIVE_MEMBER_ROLE)
        for channel in guild.text_channels:
            async for message in channel.history(limit=None, after=datetime.datetime.now() - datetime.timedelta(days=days)):
                if message.author not in active_users:
                    active_users.append(message.author)
                if message.created_at > discord.utils.utcnow() - datetime.timedelta(days=ACTIVITY_THRESHOLD):
                    if message.author not in real_active_users:
                        real_active_users.append(message.author)
        inactive_json = {}
        inactive_json_path = Path("inactive_users.json")
        print("Processing inactive users...")
        for member in guild.members:
            member: discord.Member
            if member not in active_users:
                inactive_json[member.id] = {
                    "name": member.name,
                    "discriminator": member.discriminator,
                    "joined_at": member.joined_at.isoformat(),
                    "created_at": member.created_at.isoformat(),
                }
            if member in real_active_users and ACTIVE_MEMBER_ROLE not in [role.id for role in member.roles]:
                await member.add_roles(role)
            if member not in real_active_users and ACTIVE_MEMBER_ROLE in [role.id for role in member.roles]:
                await member.remove_roles(role)
        with open(inactive_json_path, "w") as f:
            json.dump(inactive_json, f)

    @commands.slash_command(name="fetch-inactive", description="Fetch inactive users")
    async def fetch_inactive_and_active(self, ctx, days: int) -> None:
        if ctx.author.id != 546393436668952663:
            await ctx.send("You don't have permission to use this command.")
            return
        await ctx.interaction.response.defer()
        await self.fetch_inactive_users(days)
        await ctx.interaction.followup.send("Inactive users have been fetched.")
    
    @commands.slash_command(name="mention-inactive", description="Mention inactive users")
    async def mention_inactive(self, ctx) -> None:
        if ctx.author.id != 546393436668952663:
            await ctx.send("You don't have permission to use this command.")
            return
        await ctx.interaction.response.defer()
        inactive_json_path = Path("inactive_users.json")
        if not inactive_json_path.exists():
            await ctx.send("You didn't fetch inactive users yet.")
        with open(inactive_json_path, "r") as f:
            inactive_json = json.load(f)
        inactive_users = []
        for member_id, member_data in inactive_json.items():
            member: discord.Member = ctx.guild.get_member(int(member_id))
            inactive_users.append(member.mention)
        message = " ".join(inactive_users)
        for i in range(0, len(message), 2000):
            message_to_send = message[i:i+2000]
            first_mention_index = message_to_send.find("<@")
            if first_mention_index != -1:
                message_to_send = message_to_send[first_mention_index:]
            last_mention_index = message_to_send.rfind("<@")
            if last_mention_index != -1:
                message_to_send = message_to_send[:last_mention_index]
            await ctx.send(message_to_send)
        await ctx.interaction.followup.send("Inactive users have been mentioned.")
    
    @commands.slash_command(name="kick-inactive", description="Kick inactive users")
    async def kick_inactive(self, ctx, number: int) -> None:
        if ctx.author.id != 546393436668952663:
            await ctx.send("You don't have permission to use this command.")
            return
        await ctx.interaction.response.defer()
        inactive_json_path = Path("inactive_users.json")
        if not inactive_json_path.exists():
            await ctx.send("You didn't fetch inactive users yet.")
        with open(inactive_json_path, "r") as f:
            inactive_json = json.load(f)
        guild: discord.Guild = ctx.guild
        while number > 0:
            member_id = random.choice(list(inactive_json.keys()))
            member: discord.Member = guild.get_member(int(member_id))
            await member.kick(reason="Inactive user")
            del inactive_json[member_id]
            number -= 1
        await ctx.interaction.followup.send(f"{number} inactive users have been kicked.")
        inactive_json_path.unlink()
    
    @tasks.loop(hours=24)
    async def check_active_members(self) -> None:
        await self.fetch_inactive_users(30)
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.check_active_members.start()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(InactiveKick(bot))