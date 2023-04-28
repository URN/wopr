"""Main entry-point for the WOPR application."""
import logging
import sys
from datetime import datetime, timezone

import discord
from discord.ext import commands
from loguru import logger

from wopr import CONFIG

MY_GUILD = discord.Object(id=CONFIG.guild_id)


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


class BotBase(commands.Bot):
    """A base class for the bot to allow for custom attributes."""

    start_time: datetime


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

intents = discord.Intents.all()
bot = BotBase(intents=intents, command_prefix=CONFIG.prefix)


@bot.event
async def on_ready() -> None:
    """Bot on-ready function to load extensions and sync commands."""
    logger.info("Logged in as {bot.user} ({bot.user.id})", bot=bot)

    bot.start_time = datetime.now(tz=timezone.utc)

    await bot.load_extension("wopr.exts.stream")

    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)


@bot.tree.command()
async def ping(interaction: discord.Interaction) -> None:
    """Ping the bot."""
    await interaction.response.send_message("Pong! :ping_pong:")


@bot.tree.command()
async def uptime(interaction: discord.Interaction) -> None:
    """Fetch the uptime of the bot."""
    await interaction.response.send_message(
        f"Uptime: {discord.utils.format_dt(bot.start_time, style='R')}"
    )


bot.run(CONFIG.token, log_handler=None)
