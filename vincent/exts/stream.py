from datetime import datetime

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from .. import CONFIG

@app_commands.guild_only()
class Stream(commands.GroupCog):
    """Commands for working with and controlling the Icecast Server."""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def play(self, interaction: discord.Interaction):
        """Join a channel and play URN!"""
        if not interaction.user.voice:
            return await interaction.response.send_message(":x: Join a voice channel first!")

        await interaction.response.send_message(":white_check_mark: Joining!")

        vc = await interaction.user.voice.channel.connect(self_deaf=True, self_mute=False)

        vc.play(discord.FFmpegOpusAudio(CONFIG.stream_url))

    @app_commands.command()
    async def info(self, interaction: discord.Interaction):
        """Retrieve statistics on the Icecast stream"""
        async with aiohttp.ClientSession() as session:
            async with session.get(CONFIG.stats_url) as resp:
                data = (await resp.json())["icestats"]
                source = data["source"]
                embed = discord.Embed(title=f"Stream Information: {source['server_name']}", color=0x5F2A87)
                embed.add_field(name="Listeners (current)", value=source["listeners"], inline=True)
                embed.add_field(name="Listeners (peak)", value=source["listener_peak"], inline=True)
                embed.add_field(name="Bitrate", value=source["ice-bitrate"], inline=True)

                stream_start = source["stream_start_iso8601"].split("+")
                stream_start = datetime.fromisoformat(f"{stream_start[0]}+{stream_start[1][:2]}:{stream_start[1][2:]}")

                server_start = data["server_start_iso8601"].split("+")
                server_start = datetime.fromisoformat(f"{server_start[0]}+{server_start[1][:2]}:{server_start[1][2:]}")

                embed.add_field(name="Stream Start", value=discord.utils.format_dt(stream_start, style="R"), inline=True)
                embed.add_field(name="Server Start", value=discord.utils.format_dt(server_start, style="R"), inline=True)

                embed.add_field(name="Server Version", value=data["server_id"], inline=True)

                await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def stop(self, interaction: discord.Interaction):
        """Stop playing URN in the servers voice channel."""
        if vc := interaction.guild.voice_client:
            await vc.disconnect()
            await interaction.response.send_message(":white_check_mark: Leaving voice, goodbye!")
        else:
            await interaction.response.send_message(":x: Not in a voice channel!")

async def setup(bot):
    await bot.add_cog(Stream(bot))
