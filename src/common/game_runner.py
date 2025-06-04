from typing import List

from .game import Game


class GameRunner:
    """Initializes and runs One Night Ultimate Werewolf games.

    This class serves as a wrapper around the Game class, providing
    a simple interface for starting and managing game instances.
    """

    def __init__(self, player_names: List[str], ctx):
        """Initialize a new game runner.

        Args:
            player_names (List[str]): List of player names participating in the game.
            ctx: Discord context object for sending messages to the channel.
        """
        self.player_names = player_names
        self.ctx = ctx
        self.game = None

    async def run_game(self):
        """Initialize and run a game.

        Creates a new Game instance with the provided player names and context,
        then starts the game execution.
        """
        self.game = Game(self.player_names, self.ctx)

        await self.game.start()
