"""Utilities for importing assets."""
import os
import shutil

import discord
import requests
from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Assets(commands.GroupCog):
    """Commands for adding assets to Zetta."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def download_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Offer an autofilled response to download call."""
        choices = ["Beds", "Songs", "Idents"]
        return [app_commands.Choice(name=choice, value=choice) for choice in choices]

    @app_commands.command()
    @app_commands.autocomplete(type=download_autocomplete)
    async def download(
        self,
        interaction: discord.Interaction,
        attachment: str,
        type: str,
    ) -> None:
        """Download an attachment and adds it to Zetta mount."""
        if attachment.startswith("https://cdn.discordapp.com"):
            if requests.get(attachment, timeout=20).headers["content-type"] == "audio/mpeg":
                local_filename = attachment.split("/")[-1].replace("_", " ")
                path = os.path.join(f"/mnt/Imports/{type}/{local_filename}")
                with requests.get(attachment, stream=True, timeout=25) as r, open(path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                f.close()
                await interaction.response.send_message(":white_check_mark: Downloaded file")
            else:
                await interaction.response.send_message(":x: This is not an MP3 file!")

        else:
            await interaction.response.send_message(":x: Please submit a Discord attachment link")


async def setup(bot: commands.Bot) -> None:
    """Set up the assets cog."""
    await bot.add_cog(Assets(bot))
