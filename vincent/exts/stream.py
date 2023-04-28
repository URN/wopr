"""Utilities for working with Icecast."""
from datetime import datetime

import aiohttp
import discord
import humanize
from discord import app_commands
from discord.ext import commands

from vincent import CONFIG


@app_commands.guild_only()
class Stream(commands.GroupCog):
    """Commands for working with and controlling the Icecast Server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def play(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel | discord.StageChannel | None = None,
    ) -> None:
        """Join a channel and play URN."""
        if (
            not channel
            and isinstance(interaction.user, discord.Member)
            and (vs := interaction.user.voice)
        ):
            channel = vs.channel

        if not channel:
            await interaction.response.send_message(":x: Join a voice channel first!")
            return

        await interaction.response.send_message(":white_check_mark: Joining!")

        vc = await channel.connect(self_deaf=True, self_mute=False)

        vc.play(discord.FFmpegOpusAudio(CONFIG.stream_url))
        return

    @app_commands.command()
    async def info(self, interaction: discord.Interaction) -> None:
        """Retrieve statistics on the Icecast stream."""
        async with aiohttp.ClientSession() as session:
            async with session.get(CONFIG.stats_url) as resp:
                data = (await resp.json())["icestats"]
                source = data["source"]

                stream_start = source["stream_start_iso8601"].split("+")
                stream_start = datetime.fromisoformat(
                    f"{stream_start[0]}+{stream_start[1][:2]}:{stream_start[1][2:]}"
                )

                server_start = data["server_start_iso8601"].split("+")
                server_start = datetime.fromisoformat(
                    f"{server_start[0]}+{server_start[1][:2]}:{server_start[1][2:]}"
                )

                embed = discord.Embed(
                    title=f"Stream Information: {source['server_name']}", color=0x5F2A87
                )

                fields = {
                    "Listeners (current)": source["listeners"],
                    "Listeners (peak)": source["listener_peak"],
                    "Bitrate": source["ice-bitrate"],
                    "Stream Start": discord.utils.format_dt(stream_start, style="R"),
                    "Server Start": discord.utils.format_dt(server_start, style="R"),
                    "Server Version": data["server_id"],
                    "Bytes Sent": humanize.naturalsize(source["total_bytes_sent"]),
                    "Bytes Read": humanize.naturalsize(source["total_bytes_read"]),
                }

                for field, value in fields.items():
                    embed.add_field(name=field, value=value, inline=True)

                await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def stop(self, interaction: discord.Interaction) -> None:
        """Stop playing URN in the servers voice channel."""
        if interaction.guild and (vc := interaction.guild.voice_client):
            await vc.disconnect(force=True)
            await interaction.response.send_message(":white_check_mark: Leaving voice, goodbye!")
        else:
            await interaction.response.send_message(":x: Not in a voice channel!")


async def setup(bot: commands.Bot) -> None:
    """Set up the stream cog."""
    await bot.add_cog(Stream(bot))
