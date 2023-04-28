"""Main entry-point for the WOPR application."""
import logging
import sys

import discord
from discord.ext import commands
from loguru import logger

from wopr import CONFIG


class InterceptHandler(logging.Handler):
    """Intercept existing logging handlers with Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log to loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

MY_GUILD = discord.Object(id=CONFIG.guild_id)

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix=CONFIG.prefix)


@bot.event
async def on_ready() -> None:
    """Bot on-ready function to load extensions and sync commands."""
    logger.info("Logged in as {bot.user} ({bot.user.id})", bot=bot)

    await bot.load_extension("wopr.exts.stream")

    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)


@bot.tree.command()
async def ping(interaction: discord.Interaction) -> None:
    """Ping the bot."""
    await interaction.response.send_message("Pong! :ping_pong:")


bot.run(CONFIG.token, log_handler=None)
