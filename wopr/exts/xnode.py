"""Utilities for working with xnodes."""
import discord
from typing import Literal, cast
from tabulate import tabulate
from discord import app_commands
from discord.ext import commands
import asyncio
import re
import telnetlib3

from wopr import CONFIG

COMMANDS : dict = {
    "Destinations" : "DST"
}

def parse_address(addr: str) -> dict:
    """Parse destination subscription address into IP and friendly name components."""
    addr = addr.strip()
    pattern = r"^([0-9.]+)(?:\s+<([^>]+)>)?$"

    match = re.match(pattern, addr)

    if match:
        return {"ip" : match.group(1), "name" : match.group(2)}

    return {"ip" : None, "name": None}

def parse_dests(output: str) -> list[dict[str, str]]:
    """Take a raw output string and attempt to parse with a regex, returning a list of dictionaries.

    One for each destination entry in the table.
    Return [] if bad response
    """
    lines = output.split("\n")

    # if it doesn't begin with this, then it probably errored out! return empty
    if lines[0] != "BEGIN\r":
        return []

    # we match for [KEY]:[VALUE] where VALUE could include spaces
    pattern = r'(\w+):(?:["\']([^"\']*)["\']|(\S+))'

    all_dests = []
    i = 1
    # go through each line of content
    while lines[i] != "END\r":
        #try to find all key/value pairs
        matches = re.findall(pattern, lines[i].strip())

        dest_dict = {}
        for field in matches:
            """ each "field" is a 3-tuple of (KEY, value1, value2)
            value1/value2 will be empty string depending on
            the match """

            key = field[0]
            value = field[1] if field[1] else field[2]

            dest_dict[key] = value
        all_dests.append(dest_dict)
        i += 1
    return all_dests



@app_commands.guild_only()
class Xnode(commands.GroupCog):
    """Commands for gathering data from Axia X-Node."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def get_info(
        self,
        interaction: discord.Interaction,
        xnode: Literal["CTA", "St1 Microphone", "St1 Mixed Signal"],
        command: Literal["Destinations"]
    ) -> None:
        """Query X-Node with command and return parsed output to caller."""
        device_ip = CONFIG.xnode_ips[xnode]

        writer = None
        try:
            #Attempt to connect to device
            reader, writer = await asyncio.wait_for(
                telnetlib3.open_connection(device_ip, 93),
                timeout=3.0
            )

            writer.write(COMMANDS[command] + "\n")
            await writer.drain()

            # We wait for a response and process each chunk until we get to the end
            output: str = ""
            while "END" not in output:
                chunk = await asyncio.wait_for(reader.read(4096), timeout=3.0)
                if not chunk:
                    break

                # going to be naughty and assume we always get a string back
                output += cast(str, chunk)

            #Attempt to parse the received message
            parsed = parse_dests(output)
            if parsed == []:
                await interaction.response.send_message(":x: Couldn't parse response")
                return

            # Constructs us a nice 2D array of table data
            table_data = []
            for dest in parsed:
                if dest["ADDR"] == "":
                    table_data.append([dest["NAME"], "-", "-", "-"])
                else:
                    parsed_address = parse_address(dest["ADDR"])

                    # each row has a dest name, source subscription, IP and channel count
                    table_data.append([
                        dest["NAME"],
                        parsed_address["name"]
                            if parsed_address.get("name") is not None
                            else "UNKNOWN",
                        parsed_address["ip"],
                        dest["NCHN"]
                    ])

            # we need to make a table!
            table = tabulate(
                table_data,
                headers=["Destination", "Source Name", "Source IP", "No. Channels"],
                tablefmt="simple"
            )

            # final message construction
            message = (
                f"**{xnode} XNode Destination Statuses**\n"
                f"```text\n"
                f"{table}\n"
                f"```"
            )

            await interaction.response.send_message(message)

        except asyncio.TimeoutError:
            await interaction.response.send_message(":x: Connection attempt timed out")
            return

        except OSError as e:
            await interaction.response.send_message(f":x: Received network error: {e}")
            return

        finally:
            if writer:
                writer.close()

async def setup(bot: commands.Bot) -> None:
    """Set up the stream cog."""
    await bot.add_cog(Xnode(bot))
