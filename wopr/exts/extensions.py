"""Utilities for working with loaded bot extensions."""

from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Extensions(commands.GroupCog):
    """Commands for managing loaded extensions."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def load(self, interaction: discord.Interaction, extension: str) -> None:
        """Load an extension."""
        try:
            await self.bot.load_extension(f"wopr.exts.{extension}")
            await interaction.response.send_message(f":white_check_mark: Loaded `{extension}`!")
        except commands.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f":x: `{extension}` is already loaded!")
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f":x: `{extension}` not found!")
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(f":x: `{extension}` failed to load: {e}")

    @load.autocomplete("extension")
    async def ext_load_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for the extension argument."""
        return [
            app_commands.Choice(name=ext.stem.lower(), value=ext.stem.lower())
            for ext in Path("wopr/exts").glob("*.py")
            if current.lower() in ext.stem.lower()
        ]

    @app_commands.command()
    async def unload(self, interaction: discord.Interaction, extension: str) -> None:
        """Unload an extension."""
        try:
            await self.bot.unload_extension(f"wopr.exts.{extension}")
            await interaction.response.send_message(f":white_check_mark: Unloaded `{extension}`!")
        except (commands.ExtensionNotFound, commands.ExtensionNotLoaded):
            await interaction.response.send_message(f":x: `{extension}` not found!")

    @app_commands.command()
    async def reload(self, interaction: discord.Interaction, extension: str) -> None:
        """Reload an extension."""
        try:
            await self.bot.reload_extension(f"wopr.exts.{extension}")
            await interaction.response.send_message(f":white_check_mark: Reloaded `{extension}`!")
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f":x: `{extension}` is not loaded!")
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f":x: `{extension}` not found!")
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(f":x: `{extension}` failed to load: {e}")

    @reload.autocomplete("extension")
    @unload.autocomplete("extension")
    async def ext_reload_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for the extension argument."""
        return [
            app_commands.Choice(name=ext.split(".")[::-1][0], value=ext.split(".")[::-1][0])
            for ext in self.bot.extensions
            if current.lower() in ext.split(".")[::-1][0]
        ]


async def setup(bot: commands.Bot) -> None:
    """Set up the Extensions cog."""
    await bot.add_cog(Extensions(bot))
