import json
import re
from typing import Dict, List, Tuple

from ..common.config import GAME_CONFIG, LOG_PATHS, PLAYER_COLORS
from ..common.openai_client import LLMClient
from .prompt_manager import PromptManager


class ConversationManager:
    """Manages AI conversations and voting for One Night Ultimate Werewolf.

    This class handles conversation history, night actions, message generation,
    voting, and response formatting for the game.
    """

    def __init__(self):
        """Initialize the conversation manager with LLM client and prompt manager."""
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.conversation_history: List[Dict[str, str]] = []
        self.night_actions: Dict[str, str] = {}
        self._load_night_actions()

    def _load_night_actions(self):
        """Load night actions from file.

        Attempts to load night actions from the configured log file,
        initializing to empty dict if file not found or invalid.
        """
        try:
            with open(LOG_PATHS["night_actions"], "r") as f:
                self.night_actions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.night_actions = {}

    def add_to_history(self, player_id: str, content: str):
        """Add a message to conversation history.

        Args:
            player_id (str): The ID of the player making the statement.
            content (str): The content of the message.
        """
        self.conversation_history.append({"player_id": player_id, "content": content})
        self._save_conversation_history()

    def _save_conversation_history(self):
        """Save conversation history to file.

        Writes the current conversation history to the configured log file
        in JSON format.
        """
        with open(LOG_PATHS["day_conversation"], "w") as f:
            json.dump(self.conversation_history, f, indent=2)

    def build_context_messages(
        self, player, is_day_phase: bool = True
    ) -> List[Dict[str, str]]:
        """Build context messages for LLM with improved structure.

        Args:
            player: The player object requesting context.
            is_day_phase (bool, optional): Whether we're in day phase or night phase.
                Defaults to True.

        Returns:
            List[Dict[str, str]]: List of message dictionaries for the LLM.
        """
        messages = []

        game_context = self.prompt_manager.format_game_context(player.player_id)
        messages.append({"role": "system", "content": game_context})

        role_prompt = self.prompt_manager.get_role_prompt(player.assigned_role)
        messages.append({"role": "system", "content": role_prompt})

        night_action = self.night_actions.get(player.player_id, "")
        if night_action:
            messages.append(
                {"role": "system", "content": f"Your night action: {night_action}"}
            )

        if self.conversation_history:
            for msg in self.conversation_history:
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"{msg['player_id']}: {msg['content']}",
                    }
                )

        return messages

    async def generate_response(
        self, player, round_number: int, total_rounds: int, position: int
    ) -> str:
        """Generate a conversation response for the player.

        Args:
            player: The player object generating the response.
            round_number (int): Current round number.
            total_rounds (int): Total number of rounds.
            position (int): Player's position in the current round.

        Returns:
            str: The generated response.
        """
        messages = self.build_context_messages(player)

        response_prompt = self.prompt_manager.get_response_prompt(
            player.player_id, round_number, total_rounds, position
        )
        messages.append({"role": "user", "content": response_prompt})

        temperature = GAME_CONFIG["ai_temperature"]["conversation"]
        response = self.llm_client.create_completion(
            messages=messages,
            temperature=temperature,
            trace_name=f"player{player.player_id}_round{round_number}",
        )

        response = self._clean_response(response, player.player_id)

        self.add_to_history(player.player_id, response)

        return response

    async def generate_vote(self, player) -> str:
        """Generate a vote for the player.

        Args:
            player: The player object casting the vote.

        Returns:
            str: The name of the player to vote for.
        """
        messages = self.build_context_messages(player)

        vote_prompt = self.prompt_manager.get_vote_prompt()
        messages.append({"role": "user", "content": vote_prompt})

        temperature = GAME_CONFIG["ai_temperature"]["voting"]
        response = self.llm_client.create_completion(
            messages=messages,
            temperature=temperature,
            trace_name=f"vote_player{player.player_id}",
        )

        vote = response.strip()
        vote = vote.replace("'", "").replace('"', "").replace(".", "").strip()

        if " " in vote:
            for player_id in PLAYER_COLORS.keys():
                if player_id in vote:
                    return player_id

        return vote

    async def generate_tie_vote(
        self, player, tied_players: List[str], vote_results: str
    ) -> str:
        """Generate a tie-breaking vote.

        Args:
            player: The player object casting the tie-breaking vote.
            tied_players (List[str]): List of tied player IDs.
            vote_results (str): String describing the vote results.

        Returns:
            str: The name of the player to vote for.
        """
        messages = self.build_context_messages(player)

        tied_players_str = ", ".join(tied_players)
        tie_prompt = self.prompt_manager.get_tie_vote_prompt(
            tied_players_str, vote_results
        )
        messages.append({"role": "user", "content": tie_prompt})

        temperature = GAME_CONFIG["ai_temperature"]["voting"]
        response = self.llm_client.create_completion(
            messages=messages,
            temperature=temperature,
            trace_name=f"tie_vote_{player.player_id}",
        )

        vote = response.strip()
        vote = vote.replace("'", "").replace('"', "").replace(".", "").strip()

        if " " in vote:
            for player_id in tied_players:
                if player_id in vote:
                    return player_id

        return vote

    def format_discord_message(self, player_id: str, content: str) -> Tuple[str, str]:
        """Format message with colors for Discord.

        Args:
            player_id (str): The player's ID.
            content (str): The message content.

        Returns:
            Tuple[str, str]: Tuple of (colored_name, formatted_message).
        """
        color_code = PLAYER_COLORS.get(player_id, 37)

        colored_name = f"\u001b[1m\u001b[{color_code}m{player_id}\u001b[0m"

        formatted_content = self._apply_colors_to_mentions(content)

        formatted_message = f"{colored_name}: {formatted_content}"

        return colored_name, formatted_message

    def _apply_colors_to_mentions(self, text: str) -> str:
        """Apply colors to player mentions in text.

        Args:
            text (str): The text to process.

        Returns:
            str: Text with colored player mentions.
        """

        def colorize(match):
            player_id = match.group(0)
            color_code = PLAYER_COLORS.get(player_id, 37)
            return f"\u001b[{color_code}m{player_id}\u001b[0m"

        pattern = "|".join(re.escape(player_id) for player_id in PLAYER_COLORS.keys())
        return re.sub(pattern, colorize, text)

    def _clean_response(self, response: str, player_id: str) -> str:
        """Clean up the response by removing duplicate player IDs.

        Args:
            response (str): The raw response from the AI.
            player_id (str): The player's ID.

        Returns:
            str: Cleaned response.
        """
        patterns = [
            f"{player_id}: {player_id}: ",
            f"{player_id}: ",
        ]

        for pid in PLAYER_COLORS.keys():
            patterns.append(f"{player_id}: {pid}: ")

        for pattern in patterns:
            if response.startswith(pattern):
                response = response[len(pattern) :]
                break

        return response.strip()

    def _get_role_change_reminder(self, assigned_role: str) -> str:
        """Get a role-specific reminder about potential role changes.

        Args:
            assigned_role (str): The player's assigned role.

        Returns:
            str: A reminder string about potential role changes.
        """
        if assigned_role == "Robber":
            return (
                "\n\nREMINDER: If you robbed another player's card during the night, "
                "you saw what role you took. However, the Troublemaker acts after you, "
                "so you might have been swapped again without knowing it. Pay attention "
                "to the discussion to figure out if the Troublemaker affected you."
            )
        elif assigned_role == "Troublemaker":
            return (
                "\n\nREMINDER: If you swapped two players' cards, you don't know what "
                "roles you swapped - you only know WHO you swapped. Those players don't "
                "know they were swapped. You cannot swap yourself."
            )
        else:
            return (
                "\n\nIMPORTANT: Your role may have changed during the night. The Robber "
                "might have stolen your card, or the Troublemaker might have swapped you "
                "with another player. You won't know unless you deduce it from the discussion. "
                "Pay attention to conflicting claims and try to figure out if you were affected."
            )

    def clear_history(self):
        """Clear conversation history for a new game.

        Resets conversation history and night actions, then saves
        the cleared state to file.
        """
        self.conversation_history = []
        self.night_actions = {}
        self._save_conversation_history()
