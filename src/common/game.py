import json
import random
from typing import Dict, List

from ..conversation.conversation_manager import ConversationManager
from ..players.roles import create_player
from .config import GAME_CONFIG, LOG_PATHS


class Game:
    """Main game controller for One Night Ultimate Werewolf.

    This class manages the entire game flow including role assignment,
    night phase, day phase discussions, voting, and determining winners.
    """

    def __init__(self, player_names: List[str], ctx):
        """Initialize a new game instance.

        Args:
            player_names (List[str]): List of player names participating in the game.
            ctx: Discord context object for sending messages to the channel.
        """
        self.player_names = player_names
        self.ctx = ctx
        self.players: List = []
        self.center_roles: List[str] = []
        self.conversation_manager = ConversationManager()
        self.phase = "setup"

    async def start(self):
        """Start a new game.

        Executes the complete game flow: role assignment, night phase,
        day phase, voting phase, and game end.
        """
        await self.ctx.send("🎮 **Game Starting!**\n")

        self._initialize_logs()

        await self._assign_roles()
        await self._night_phase()
        await self._day_phase()
        await self._voting_phase()
        await self._end_game()

    def _initialize_logs(self):
        """Initialize all log files for a new game.

        Creates or clears all game log files including night actions,
        day conversation, voting results, and game recap files.
        """
        with open(LOG_PATHS["night_actions"], "w") as f:
            json.dump({}, f)

        with open(LOG_PATHS["day_conversation"], "w") as f:
            json.dump([], f)

        with open(LOG_PATHS["voting_results"], "w") as f:
            f.write("=== One Night Ultimate Werewolf - Voting Results ===\n\n")

        with open(LOG_PATHS["game_recap"], "w") as f:
            f.write("")

        self.conversation_manager.clear_history()

    async def _assign_roles(self):
        """Create players and randomly assign roles.

        Shuffles available roles and assigns them to players, with
        remaining roles placed in the center pile.
        """
        self.phase = "role_assignment"

        all_roles = GAME_CONFIG["roles"].copy()
        random.shuffle(all_roles)

        self.players = []
        for player_name in self.player_names:
            role = all_roles.pop()
            player = create_player(role, player_name, self)
            self.players.append(player)

        self.center_roles = all_roles

        await self.ctx.send("✅ **Roles have been assigned!**\n")

    async def _night_phase(self):
        """Execute night phase actions.

        Processes night actions for all roles in the correct order:
        Werewolf, Seer, Robber, Troublemaker, then Villagers.
        """
        self.phase = "night"
        await self.ctx.send("🌙 **Night Phase**\nEveryone close your eyes...\n")

        role_order = ["Werewolf", "Seer", "Robber", "Troublemaker"]

        for role in role_order:
            role_players = [p for p in self.players if p.assigned_role == role]
            for player in role_players:
                await player.perform_night_action()

        villagers = [p for p in self.players if p.assigned_role == "Villager"]
        for villager in villagers:
            await villager.perform_night_action()

        self.conversation_manager._load_night_actions()

        await self.ctx.send("☀️ **Dawn breaks! Everyone wake up!**\n")

    async def _day_phase(self):
        """Execute day phase discussions.

        Manages multiple rounds of player discussions where each player
        participates in conversation to gather information and form suspicions.
        """
        self.phase = "day"
        await self.ctx.send("💬 **Day Phase - Discussion Time!**\n")

        total_rounds = GAME_CONFIG["conversation_rounds"]

        for round_num in range(1, total_rounds + 1):
            await self.ctx.send(f"\n**📢 Discussion Round {round_num}/{total_rounds}**")

            round_players = self.players.copy()
            random.shuffle(round_players)

            for position, player in enumerate(round_players, 1):
                await player.participate_in_conversation(
                    self.conversation_manager, round_num, total_rounds, position
                )

        await self.ctx.send("\n**Discussion phase ended!**\n")

    async def _voting_phase(self):
        """Execute voting phase.

        Collects votes from all players and handles tie-breaking votes
        until a single player is eliminated.
        """
        self.phase = "voting"
        await self.ctx.send(
            "🗳️ **Voting Phase**\nTime to vote for who you think is a Werewolf!\n"
        )

        vote_count = await self._collect_votes()

        while len(self._get_max_voted_players(vote_count)) > 1:
            await self._handle_tie_vote(vote_count)
            vote_count = await self._collect_votes(is_tie_breaker=True)

        await self._announce_results(vote_count)

    async def _collect_votes(self, is_tie_breaker: bool = False) -> Dict:
        """Collect votes from all players.

        Args:
            is_tie_breaker (bool, optional): Whether this is a tie-breaking vote.
                Defaults to False.

        Returns:
            Dict: Dictionary mapping player objects to their vote counts.
        """
        vote_count = {player: 0 for player in self.players}
        player_dict = {p.player_id: p for p in self.players}

        for player in self.players:
            if is_tie_breaker:
                tied_players = [
                    p.player_id for p in self._get_max_voted_players(vote_count)
                ]
                vote_results = self._format_vote_results(vote_count)
                vote = await player.cast_tie_vote(
                    self.conversation_manager, tied_players, vote_results
                )
            else:
                vote = await player.cast_vote(self.conversation_manager)

            if vote in player_dict:
                vote_count[player_dict[vote]] += 1
            else:
                await self.ctx.send(f"⚠️ Invalid vote from {player.player_id}: {vote}")

        return vote_count

    def _get_max_voted_players(self, vote_count: Dict) -> List:
        """Get players with the most votes.

        Args:
            vote_count (Dict): Dictionary mapping players to their vote counts.

        Returns:
            List: List of player objects who received the maximum number of votes.
        """
        if not vote_count:
            return []

        max_votes = max(vote_count.values())
        return [player for player, votes in vote_count.items() if votes == max_votes]

    def _format_vote_results(self, vote_count: Dict) -> str:
        """Format vote results as a string.

        Args:
            vote_count (Dict): Dictionary mapping players to their vote counts.

        Returns:
            str: Formatted string showing each player and their vote count.
        """
        results = []
        for player, votes in vote_count.items():
            results.append(f"{player.player_id}: {votes} vote(s)")
        return ", ".join(results)

    async def _handle_tie_vote(self, vote_count: Dict):
        """Handle a tie in voting.

        Announces the tie and prepares for a tie-breaking vote round.

        Args:
            vote_count (Dict): Dictionary mapping players to their vote counts.
        """
        tied_players = self._get_max_voted_players(vote_count)
        await self.ctx.send("\n⚖️ **It's a tie!**")

        for player in self.players:
            await self.ctx.send(f"{player.player_id}: {vote_count[player]} vote(s)")

        tied_names = [p.player_id for p in tied_players]
        await self.ctx.send(f"\n**Tied players:** {', '.join(tied_names)}")
        await self.ctx.send("**Additional voting round required!**\n")

    async def _announce_results(self, vote_count: Dict):
        """Announce game results.

        Displays final vote counts, determines the winner, and logs
        all results to the voting results file.

        Args:
            vote_count (Dict): Dictionary mapping players to their vote counts.
        """
        await self.ctx.send("\n🏁 **Final Results**\n")

        with open(LOG_PATHS["voting_results"], "a") as f:
            f.write("Final Vote Count:\n")

            for player in self.players:
                votes = vote_count[player]
                result_line = (
                    f"{player.player_id} "
                    f"(Started as: {player.assigned_role}, "
                    f"Ended as: {player.current_role}): "
                    f"{votes} vote(s)"
                )

                await self.ctx.send(result_line)
                f.write(result_line + "\n")

        eliminated_player = max(vote_count, key=vote_count.get)
        winner = self._determine_winner(eliminated_player)

        if winner == "Village":
            await self.ctx.send("\n🏆 **Village Team Wins!** 🎉")
            result_text = "Game Result: Village Team Victory!"
        else:
            await self.ctx.send("\n🐺 **Werewolf Team Wins!** 🎉")
            result_text = "Game Result: Werewolf Team Victory!"

        with open(LOG_PATHS["voting_results"], "a") as f:
            f.write(f"\n{result_text}\n")

    def _determine_winner(self, eliminated_player) -> str:
        """Determine which team won.

        Args:
            eliminated_player: The player object that was eliminated by voting.

        Returns:
            str: "Village" if the village team won, "Werewolf" if werewolf team won.
        """
        if eliminated_player.current_role == "Werewolf":
            return "Village"
        else:
            return "Werewolf"

    async def _end_game(self):
        """Clean up and end the game.

        Sets the game phase to ended and sends a final game over message.
        """
        self.phase = "ended"
        await self.ctx.send("\n🎮 **Game Over!**\nThanks for playing!")
