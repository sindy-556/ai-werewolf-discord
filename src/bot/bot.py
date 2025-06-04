import asyncio
import logging

import discord
from discord.ext import commands

from ..common.config import COMMAND_PREFIX, DISCORD_TOKEN
from .commands import CustomHelpCommand, WerewolfCommands

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WerewolfBot")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX, intents=intents, help_command=CustomHelpCommand()
)


@bot.event
async def on_ready():
    """Called when the bot is ready."""

    logger.info(f"Bot logged in as {bot.user}")
    logger.info(f"Connected to {len(bot.guilds)} guilds")

    await bot.change_presence(
        activity=discord.Game(name="One Night Ultimate Werewolf | !help")
    )


@bot.event
async def on_command_error(ctx, error):
    """Global error handler.

    Args:
        ctx: The command context.
        error: The error that occurred.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.send("❌ An unexpected error occurred.")


async def main():
    """Main function to run the bot."""
    async with bot:
        await bot.add_cog(WerewolfCommands(bot))
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error(
            "Discord token not found! Please set DISCORD_TOKEN in environment or config.py"
        )
        exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
