import random

from .base import Player


class Werewolf(Player):
    """Werewolf role implementation."""

    def __init__(self, player_id: str, game):
        super().__init__(player_id, game)
        self.assigned_role = "Werewolf"
        self.current_role = "Werewolf"

    async def perform_night_action(self) -> str:
        """Werewolves see each other or check center if alone.

        Returns:
            str: Action description of what the werewolf saw.
        """
        other_werewolves = [
            p for p in self.game.players if p.assigned_role == "Werewolf" and p != self
        ]

        if other_werewolves:
            werewolf_ids = [w.player_id for w in other_werewolves]
            action = f"I have seen that players {werewolf_ids} are werewolves."
        else:
            center_card = random.choice(self.game.center_roles)
            action = (
                f"I am the only werewolf. I have seen the center card: {center_card}."
            )

        self.record_night_action(action)
        return action


class Seer(Player):
    """Seer role implementation."""

    def __init__(self, player_id: str, game):
        super().__init__(player_id, game)
        self.assigned_role = "Seer"
        self.current_role = "Seer"

    async def perform_night_action(self) -> str:
        """Seer looks at another player's card or two center cards.

        Returns:
            str: Action description of what the seer saw.
        """
        if random.random() < 0.5:
            other_players = [p for p in self.game.players if p != self]
            target = random.choice(other_players)
            action = f"I have seen that player {target.player_id} is a {target.assigned_role}."
        else:
            center_cards = random.sample(self.game.center_roles, 2)
            action = f"I have seen the center cards: {center_cards}."

        self.record_night_action(action)
        return action


class Robber(Player):
    """Robber role implementation."""

    def __init__(self, player_id: str, game):
        super().__init__(player_id, game)
        self.assigned_role = "Robber"
        self.current_role = "Robber"

    async def perform_night_action(self) -> str:
        """Robber may swap roles with another player.

        Returns:
            str: Action description of what the robber did.
        """
        if random.random() < 0.8:
            other_players = [p for p in self.game.players if p != self]
            target = random.choice(other_players)

            stolen_role = target.current_role
            target.current_role = self.current_role
            self.current_role = stolen_role

            action = f"I swapped roles with player {target.player_id} and now I am a {self.current_role}."
        else:
            action = "I had the opportunity to swap but chose not to do anything."

        self.record_night_action(action)
        return action


class Troublemaker(Player):
    """Troublemaker role implementation."""

    def __init__(self, player_id: str, game):
        super().__init__(player_id, game)
        self.assigned_role = "Troublemaker"
        self.current_role = "Troublemaker"

    async def perform_night_action(self) -> str:
        """Troublemaker may swap two other players' roles.

        Returns:
            str: Action description of what the troublemaker did.
        """
        if random.random() < 0.5:
            other_players = [p for p in self.game.players if p != self]
            if len(other_players) >= 2:
                targets = random.sample(other_players, 2)

                targets[0].current_role, targets[1].current_role = (
                    targets[1].current_role,
                    targets[0].current_role,
                )

                action = (
                    f"I swapped roles between player {targets[0].player_id} "
                    f"and player {targets[1].player_id}."
                )
            else:
                action = "Not enough players to swap roles."
        else:
            action = "I had the opportunity to swap between players but chose not to do anything."

        self.record_night_action(action)
        return action


class Villager(Player):
    """Villager role implementation."""

    def __init__(self, player_id: str, game):
        super().__init__(player_id, game)
        self.assigned_role = "Villager"
        self.current_role = "Villager"

    async def perform_night_action(self) -> str:
        """Villagers do nothing at night.

        Returns:
            str: Action description indicating no action was taken.
        """
        action = "As a villager, I did nothing during the night."
        self.record_night_action(action)
        return action


def create_player(role: str, player_id: str, game) -> Player:
    """Create a player with the specified role.

    Args:
        role: The role name.
        player_id: The player's ID.
        game: Reference to the game instance.

    Returns:
        A Player instance of the appropriate type.

    Raises:
        ValueError: If the role is unknown.
    """
    role_classes = {
        "Werewolf": Werewolf,
        "Seer": Seer,
        "Robber": Robber,
        "Troublemaker": Troublemaker,
        "Villager": Villager,
    }

    role_class = role_classes.get(role)
    if not role_class:
        raise ValueError(f"Unknown role: {role}")

    return role_class(player_id, game)
