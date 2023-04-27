#!/usr/bin/env python3

from typing import Optional
import logging
import sys

import discord
from discord.ext import commands
from loguru import logger

from vincent import CONFIG

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

MY_GUILD = discord.Object(id=CONFIG.guild_id)

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix=CONFIG.prefix)


@client.event
async def on_ready():
    logger.info("Logged in as {client.user} ({client.user.id})", client=client)

    await client.load_extension("vincent.exts.stream")

    client.tree.copy_global_to(guild=MY_GUILD)
    await client.tree.sync(guild=MY_GUILD)

client.run(CONFIG.token, log_handler=None)
