"""Utilities for working with the iQx mixing frame."""

import aiohttp
import discord
import humanize
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from wopr import CONFIG


@app_commands.guild_only()
class IQX(commands.GroupCog, group_name="iqx"):
    """Commands for working with and controlling the iQx mixing frame."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def info(self, interaction: discord.Interaction) -> None:
        """Retrieve statistics from iQx."""
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(CONFIG.iqx_username, CONFIG.iqx_password)
        ) as session:
            async with session.get(CONFIG.iqx_url) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")

                info_table = soup.findAll("table")[4]
                data = {}
                for row in info_table.findAll("tr"):
                    data[row.findAll("td")[0].text[:-1]] = row.findAll("td")[1].text

                to_embed = {
                    "Uptime": data["Uptime"],
                    "CPU usage": data["CPU usage"],
                    "DSP usage": data["DSP usage"],
                    "Net Link": data["Net Link"],
                }

                info_embed = discord.Embed(title="iQx Information", color=0x5F2A87)

                info_embed.set_footer(text=f"Powered by iQx on {data['Kernel']}")

                for key, value in to_embed.items():
                    info_embed.add_field(name=key, value=value, inline=True)

                net_embed = discord.Embed(title="iQx Network Information")

                net_usage_tx, net_usage_rx = (v[3:] for v in data["Net Usage"].split(", "))
                net_bytes_tx, net_bytes_rx = (int(v[3:]) for v in data["Net Bytes"].split(", "))
                packet_tx, packet_rx = (int(v[3:]) for v in data["Net Packets"].split(", "))
                net_drops_tx, net_drops_rx = (int(v[3:]) for v in data["Net Drops"].split(", "))
                net_errors_tx, net_errors_rx = (int(v[3:]) for v in data["Net Errors"].split(", "))

                net_info = {
                    "Usage TX": net_usage_tx,
                    "Usage RX": net_usage_rx,
                    "Data TX": humanize.naturalsize(net_bytes_tx),
                    "Data RX": humanize.naturalsize(net_bytes_rx),
                    "Packet TX": humanize.intword(packet_tx),
                    "Packet RX": humanize.intword(packet_rx),
                    "Drops TX": humanize.intword(net_drops_tx),
                    "Drops RX": humanize.intword(net_drops_rx),
                    "Errors TX": humanize.intword(net_errors_tx),
                    "Errors RX": humanize.intword(net_errors_rx),
                }

                for key, value in net_info.items():
                    net_embed.add_field(name=key, value=value, inline=True)

        await interaction.response.send_message(embeds=[info_embed, net_embed])


async def setup(bot: commands.Bot) -> None:
    """Set up the iQx cog."""
    await bot.add_cog(IQX(bot))
