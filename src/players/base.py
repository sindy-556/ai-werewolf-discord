import json
from abc import ABC, abstractmethod

from ..common.config import LOG_PATHS


class Player(ABC):
    """Base class for all players in One Night Ultimate Werewolf.

    This abstract class defines the common interface and functionality
    for all player types in the game, including night actions, conversation
    participation, and voting.
    """

    def __init__(self, player_id: str, game):
        """Initialize a new player.

        Args:
            player_id (str): Unique identifier for the player.
            game: The game instance this player belongs to.
        """
        self.player_id = player_id
        self.game = game
        self.assigned_role = None
        self.current_role = None

    @abstractmethod
    async def perform_night_action(self) -> str:
        """Perform the player's night action.

        Returns:
            str: A string describing the action taken.
        """
        pass

    def record_night_action(self, action: str):
        """Record the night action to the log.

        Args:
            action (str): Description of the night action performed.
        """
        # Load existing actions
        try:
            with open(LOG_PATHS["night_actions"], "r") as f:
                night_actions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            night_actions = {}

        # Add this player's action
        night_actions[self.player_id] = action

        # Save back to file
        with open(LOG_PATHS["night_actions"], "w") as f:
            json.dump(night_actions, f, indent=2)

    async def participate_in_conversation(
        self, conversation_manager, round_number: int, total_rounds: int, position: int
    ):
        """Participate in day phase conversation.

        Args:
            conversation_manager: The conversation manager instance.
            round_number (int): Current round number.
            total_rounds (int): Total number of rounds.
            position (int): Player's position in the current round.
        """
        response = await conversation_manager.generate_response(
            self, round_number, total_rounds, position
        )

        _, formatted_message = conversation_manager.format_discord_message(
            self.player_id, response
        )
        await self.game.ctx.send(f"```ansi\n{formatted_message}\n```")

    async def cast_vote(self, conversation_manager) -> str:
        """Cast a vote for who the werewolf is.

        Args:
            conversation_manager: The conversation manager instance.

        Returns:
            str: The player ID of who to vote for.
        """
        return await conversation_manager.generate_vote(self)

    async def cast_tie_vote(
        self, conversation_manager, tied_players: list, vote_results: str
    ) -> str:
        """Cast a tie-breaking vote.

        Args:
            conversation_manager: The conversation manager instance.
            tied_players (list): List of players who are tied.
            vote_results (str): String describing the vote results.

        Returns:
            str: The player ID of who to vote for.
        """
        return await conversation_manager.generate_tie_vote(
            self, tied_players, vote_results
        )
