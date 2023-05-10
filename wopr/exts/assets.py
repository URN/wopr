"""Utilities for importing assets."""
import os
from typing import Literal

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Assets(commands.GroupCog):
    """Commands for adding assets to Zetta."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def download(
        self,
        interaction: discord.Interaction,
        type: Literal["Idents", "Songs", "Beds"],
        attachment: str,
    ) -> None:
        """Download an attachment and adds it to Zetta mount."""
        if not attachment.startswith("https://cdn.discordapp.com"):
            await interaction.response.send_message(":x: Please submit a Discord attachment link")
            return

        async with aiohttp.ClientSession() as session:
            async with session.head(attachment) as resp:
                if resp.headers["content-type"] != "audio/mpeg":
                    await interaction.response.send_message(":x: This is not an MP3 file!")
                    return

            local_filename = attachment.split("/")[-1].replace("_", " ")
            path = os.path.join(f"/mnt/Imports/{type}/{local_filename}")

            async with session.get(attachment) as resp:
                with open(path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        f.write(chunk)

        await interaction.response.send_message(":white_check_mark: Downloaded file")


async def setup(bot: commands.Bot) -> None:
    """Set up the assets cog."""
    await bot.add_cog(Assets(bot))
