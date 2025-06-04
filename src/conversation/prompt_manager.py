from pathlib import Path
from typing import Dict

from ..common.config import PROMPT_PATHS


class PromptManager:
    """Manages loading and caching of game prompts."""

    def __init__(self):
        """Initialize the prompt manager and load all prompts into cache."""
        self._prompt_cache: Dict[str, str] = {}
        self._load_all_prompts()

    def _load_all_prompts(self):
        """Load all prompts into cache on initialization.

        Loads game prompts and role-specific prompts from their respective
        file paths into the internal cache for quick access.
        """
        # Load game prompts
        for prompt_name, prompt_path in PROMPT_PATHS.items():
            if prompt_name == "roles":
                # Handle role prompts separately
                for role_name, role_path in prompt_path.items():
                    cache_key = f"role_{role_name}"
                    self._prompt_cache[cache_key] = self._read_file(role_path)
            else:
                self._prompt_cache[prompt_name] = self._read_file(prompt_path)

    def _read_file(self, path: Path) -> str:
        """Read a file and return its contents.

        Args:
            path (Path): The file path to read from.

        Returns:
            str: The contents of the file, or empty string if file not found.
        """
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file not found: {path}")
            return ""

    def get_game_prompt(self) -> str:
        """Get the main game rules prompt.

        Returns:
            str: The main game rules prompt text.
        """
        return self._prompt_cache.get("game_rule", "")

    def get_role_prompt(self, role: str) -> str:
        """Get prompt for a specific role.

        Args:
            role (str): The role name to get the prompt for.

        Returns:
            str: The role-specific prompt text.
        """
        return self._prompt_cache.get(f"role_{role}", "")

    def get_response_prompt(
        self, player_id: str, round_number: int, total_rounds: int, count: int
    ) -> str:
        """Get formatted response prompt for conversation.

        Args:
            player_id (str): The ID of the player.
            round_number (int): Current round number.
            total_rounds (int): Total number of rounds.
            count (int): Player's position in the current round.

        Returns:
            str: The formatted response prompt with context information.
        """
        base_prompt = self._prompt_cache.get("response_rule", "")
        return (
            f"{player_id}, {base_prompt}\n"
            f"Please note you are now in position {count} "
            f"in discussion round {round_number} of {total_rounds} total rounds. "
            f"Please adjust your strategy accordingly."
        )

    def get_vote_prompt(self) -> str:
        """Get voting prompt.

        Returns:
            str: The voting prompt text.
        """
        return self._prompt_cache.get("vote_rule", "")

    def get_tie_vote_prompt(self, tied_players: str, vote_results: str) -> str:
        """Get tie-breaking vote prompt.

        Args:
            tied_players (str): Comma-separated string of tied player names.
            vote_results (str): String describing the previous vote results.

        Returns:
            str: The formatted tie-breaking vote prompt.
        """
        base_prompt = self._prompt_cache.get("vote_rule_tie", "")
        return (
            f"The last round of voting results are: {vote_results}\n"
            f"These players are tied: [{tied_players}]\n"
            f"{base_prompt}"
        )

    def format_game_context(self, player_id: str) -> str:
        """Format the game context with player information.

        Args:
            player_id (str): The ID of the player.

        Returns:
            str: The formatted game context including player identification.
        """
        game_prompt = self.get_game_prompt()
        return f"{game_prompt}\n\nYou are {player_id} in this game."
