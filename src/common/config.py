import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
LOGS_DIR = BASE_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX = "!"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

GAME_CONFIG = {
    "total_players": 5,
    "total_cards": 8,
    "roles": [
        "Werewolf",
        "Werewolf",
        "Seer",
        "Robber",
        "Troublemaker",
        "Villager",
        "Villager",
        "Villager",
    ],
    "conversation_rounds": 3,
    "ai_temperature": {"conversation": 0.8, "voting": 0.2},
}

PLAYER_COLORS = {
    "AI_P1": 31,  # Red
    "AI_P2": 32,  # Green
    "AI_P3": 33,  # Yellow
    "AI_P4": 34,  # Blue
    "AI_P5": 35,  # Pink
}

LOG_PATHS = {
    "night_actions": LOGS_DIR / "night_actions.json",
    "day_conversation": LOGS_DIR / "day_conversation.json",
    "voting_results": LOGS_DIR / "voting_results.txt",
    "game_recap": LOGS_DIR / "game_recap.txt",
}

PROMPT_PATHS = {
    "game_rule": PROMPTS_DIR / "game_prompts" / "game_rule.txt",
    "response_rule": PROMPTS_DIR / "game_prompts" / "response_rule.txt",
    "vote_rule": PROMPTS_DIR / "game_prompts" / "vote_rule.txt",
    "vote_rule_tie": PROMPTS_DIR / "game_prompts" / "vote_rule_tie.txt",
    "roles": {
        "Werewolf": PROMPTS_DIR / "role_prompts" / "werewolf_role.txt",
        "Seer": PROMPTS_DIR / "role_prompts" / "seer_role.txt",
        "Robber": PROMPTS_DIR / "role_prompts" / "robber_role.txt",
        "Troublemaker": PROMPTS_DIR / "role_prompts" / "troublemaker_role.txt",
        "Villager": PROMPTS_DIR / "role_prompts" / "villager_role.txt",
    },
}
