"""Utilities for importing assets."""
import tempfile

import discord
import requests
from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Assets(commands.GroupCog):
    """Commands for adding assets to Zetta."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def linkcheck(
        self,
        interaction: discord.Interaction,
        attachment: str,
    ) -> None:
        """Download an attachment and adds it to Zetta mount."""
        temp = tempfile.TemporaryFile()

        if attachment.startswith("https://cdn.discordapp.com"):
            temp.write(requests.get(attachment, timeout=5).content)
            temp.close()
            await interaction.response.send_message("This is a correct link")

        else:
            await interaction.response.send_message(":x: Please submit a Discord attachment link")


async def setup(bot: commands.Bot) -> None:
    """Set up the assets cog."""
    await bot.add_cog(Assets(bot))
