import discord
from discord.ext import commands

from ..common.game_runner import GameRunner


class WerewolfCommands(commands.Cog):
    """Commands for the Werewolf bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play")
    async def ai_only_game(self, ctx):
        """Start an AI-only game with 5 players.

        Args:
            ctx: The command context.
        """
        await ctx.send("🎮 Starting an AI-only game...")

        player_names = ["AI_P1", "AI_P2", "AI_P3", "AI_P4", "AI_P5"]
        game_runner = GameRunner(player_names, ctx)

        try:
            await game_runner.run_game()
        except Exception as e:
            await ctx.send(f"❌ Error running game: {str(e)}")
            raise

    @commands.command(name="rules")
    async def show_rules(self, ctx):
        """Display the game rules.

        Args:
            ctx: The command context.
        """
        embed = discord.Embed(
            title="🐺 One Night Ultimate Werewolf Rules",
            description="Quick guide for 5 players",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="📋 Setup",
            value=(
                "• 8 cards total: 2 Werewolves, 1 Seer, 1 Robber, "
                "1 Troublemaker, 3 Villagers\n"
                "• Each player gets 1 card\n"
                "• 3 cards remain in the center"
            ),
            inline=False,
        )

        embed.add_field(
            name="🌙 Night Phase",
            value=(
                "**Werewolves:** See each other (or check center if alone)\n"
                "**Seer:** Look at 1 player's card OR 2 center cards\n"
                "**Robber:** Swap with another player and see new role\n"
                "**Troublemaker:** Swap 2 other players' cards\n"
                "**Villagers:** Do nothing"
            ),
            inline=False,
        )

        embed.add_field(
            name="☀️ Day Phase",
            value=(
                "• Discuss and deduce who the Werewolves are\n"
                "• Players can lie, tell truth, or bluff\n"
                "• Use information from night actions wisely"
            ),
            inline=False,
        )

        embed.add_field(
            name="🗳️ Voting",
            value=(
                "• Vote for the suspected Werewolf\n"
                "• Player with most votes is eliminated\n"
                "• **Village wins** if a Werewolf is eliminated\n"
                "• **Werewolves win** if no Werewolf is eliminated"
            ),
            inline=False,
        )

        embed.set_footer(
            text="For detailed rules: https://www.ultraboardgames.com/one-night-ultimate-werewolf/game-rules.php"
        )

        await ctx.send(embed=embed)

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: str):
        """Clear messages from the channel.

        Args:
            ctx: The command context.
            amount: Number of messages to clear or "all" for all messages.
        """
        if amount.lower() == "all":
            await ctx.send("🧹 Clearing all messages...", delete_after=3)

            deleted_total = 0
            while True:
                deleted = await ctx.channel.purge(limit=100)
                deleted_total += len(deleted)
                if len(deleted) == 0:
                    break

            await ctx.send(f"✅ Cleared {deleted_total} messages!", delete_after=3)

        else:
            try:
                num = int(amount)
                if num <= 0:
                    await ctx.send(
                        "❌ Please specify a positive number", delete_after=5
                    )
                    return

                deleted = await ctx.channel.purge(
                    limit=num + 1
                )  # +1 to include command
                await ctx.send(
                    f"✅ Cleared {len(deleted) - 1} messages", delete_after=3
                )

            except ValueError:
                await ctx.send(
                    '❌ Invalid input. Use a number or "all"', delete_after=5
                )

    @clear_messages.error
    async def clear_error(self, ctx, error):
        """Handle errors for the clear command.

        Args:
            ctx: The command context.
            error: The error that occurred.
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Manage Messages permission to use this command")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")


class CustomHelpCommand(commands.MinimalHelpCommand):
    """Custom help command with better formatting."""

    async def send_pages(self):
        """Send paginated help content."""
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=discord.Color.blue())
            await destination.send(embed=embed)

    async def send_bot_help(self, mapping):
        """Send the main help message.

        Args:
            mapping: Command mapping from the bot.
        """
        embed = discord.Embed(
            title="🐺 Werewolf Bot Commands",
            description="List of available commands:",
            color=discord.Color.blue(),
        )

        embed.add_field(name="!help", value="Shows this help message", inline=False)

        embed.add_field(
            name="!play", value="Start an AI-only game with 5 players", inline=False
        )

        embed.add_field(name="!rules", value="Display the game rules", inline=False)

        embed.add_field(
            name="!clear <number> or !clear all",
            value="Clear messages from the channel (requires permissions)",
            inline=False,
        )

        embed.set_footer(text="🤖 Currently supports 5 AI players per game")

        channel = self.get_destination()
        await channel.send(embed=embed)


def setup(bot):
    """Setup function for loading the cog.

    Args:
        bot: The Discord bot instance.
    """
    bot.add_cog(WerewolfCommands(bot))
    bot.help_command = CustomHelpCommand()
