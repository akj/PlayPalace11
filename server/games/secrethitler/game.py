"""Secret Hitler game implementation — skeleton."""

from dataclasses import dataclass, field

from ..base import Game, Player
from ..registry import register_game


@dataclass
@register_game
class SecretHitler(Game):
    """Secret Hitler — social-deduction legislative game, 5–10 players."""

    players: list[Player] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Secret Hitler"

    @classmethod
    def get_type(cls) -> str:
        return "secrethitler"

    @classmethod
    def get_category(cls) -> str:
        return "category-social-deduction"

    @classmethod
    def get_min_players(cls) -> int:
        return 5

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> Player:
        return Player(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
