"""Monopoly game scaffold wired to generated preset artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.bot_helper import BotHelper
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.options import MenuOption, option_field
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from .presets import (
    DEFAULT_PRESET_ID,
    MonopolyPreset,
    get_available_preset_ids as _catalog_preset_ids,
    get_default_preset_id as _catalog_default_preset_id,
    get_preset as _catalog_get_preset,
)


PRESET_LABEL_KEYS = {
    "classic_standard": "monopoly-preset-classic-standard",
    "junior": "monopoly-preset-junior",
    "cheaters": "monopoly-preset-cheaters",
    "electronic_banking": "monopoly-preset-electronic-banking",
    "voice_banking": "monopoly-preset-voice-banking",
    "sore_losers": "monopoly-preset-sore-losers",
    "speed": "monopoly-preset-speed",
    "builder": "monopoly-preset-builder",
    "city": "monopoly-preset-city",
    "bid_card_game": "monopoly-preset-bid-card-game",
    "deal_card_game": "monopoly-preset-deal-card-game",
    "knockout": "monopoly-preset-knockout",
    "free_parking_jackpot": "monopoly-preset-free-parking-jackpot",
}


@dataclass(frozen=True)
class MonopolySpace:
    """A board space on the classic Monopoly board."""

    index: int
    space_id: str
    name: str
    kind: str
    price: int = 0
    rent: int = 0
    color_group: str = ""
    house_cost: int = 0
    rents: tuple[int, ...] = ()


CLASSIC_STANDARD_BOARD = [
    MonopolySpace(0, "go", "GO", "start"),
    MonopolySpace(
        1,
        "mediterranean_avenue",
        "Mediterranean Avenue",
        "property",
        60,
        2,
        color_group="brown",
        house_cost=50,
        rents=(2, 10, 30, 90, 160, 250),
    ),
    MonopolySpace(2, "community_chest_1", "Community Chest", "community_chest"),
    MonopolySpace(
        3,
        "baltic_avenue",
        "Baltic Avenue",
        "property",
        60,
        4,
        color_group="brown",
        house_cost=50,
        rents=(4, 20, 60, 180, 320, 450),
    ),
    MonopolySpace(4, "income_tax", "Income Tax", "tax"),
    MonopolySpace(5, "reading_railroad", "Reading Railroad", "railroad", 200, 25),
    MonopolySpace(
        6,
        "oriental_avenue",
        "Oriental Avenue",
        "property",
        100,
        6,
        color_group="light_blue",
        house_cost=50,
        rents=(6, 30, 90, 270, 400, 550),
    ),
    MonopolySpace(7, "chance_1", "Chance", "chance"),
    MonopolySpace(
        8,
        "vermont_avenue",
        "Vermont Avenue",
        "property",
        100,
        6,
        color_group="light_blue",
        house_cost=50,
        rents=(6, 30, 90, 270, 400, 550),
    ),
    MonopolySpace(
        9,
        "connecticut_avenue",
        "Connecticut Avenue",
        "property",
        120,
        8,
        color_group="light_blue",
        house_cost=50,
        rents=(8, 40, 100, 300, 450, 600),
    ),
    MonopolySpace(10, "jail", "Jail / Just Visiting", "jail"),
    MonopolySpace(
        11,
        "st_charles_place",
        "St. Charles Place",
        "property",
        140,
        10,
        color_group="pink",
        house_cost=100,
        rents=(10, 50, 150, 450, 625, 750),
    ),
    MonopolySpace(12, "electric_company", "Electric Company", "utility", 150, 20),
    MonopolySpace(
        13,
        "states_avenue",
        "States Avenue",
        "property",
        140,
        10,
        color_group="pink",
        house_cost=100,
        rents=(10, 50, 150, 450, 625, 750),
    ),
    MonopolySpace(
        14,
        "virginia_avenue",
        "Virginia Avenue",
        "property",
        160,
        12,
        color_group="pink",
        house_cost=100,
        rents=(12, 60, 180, 500, 700, 900),
    ),
    MonopolySpace(15, "pennsylvania_railroad", "Pennsylvania Railroad", "railroad", 200, 25),
    MonopolySpace(
        16,
        "st_james_place",
        "St. James Place",
        "property",
        180,
        14,
        color_group="orange",
        house_cost=100,
        rents=(14, 70, 200, 550, 750, 950),
    ),
    MonopolySpace(17, "community_chest_2", "Community Chest", "community_chest"),
    MonopolySpace(
        18,
        "tennessee_avenue",
        "Tennessee Avenue",
        "property",
        180,
        14,
        color_group="orange",
        house_cost=100,
        rents=(14, 70, 200, 550, 750, 950),
    ),
    MonopolySpace(
        19,
        "new_york_avenue",
        "New York Avenue",
        "property",
        200,
        16,
        color_group="orange",
        house_cost=100,
        rents=(16, 80, 220, 600, 800, 1000),
    ),
    MonopolySpace(20, "free_parking", "Free Parking", "free_parking"),
    MonopolySpace(
        21,
        "kentucky_avenue",
        "Kentucky Avenue",
        "property",
        220,
        18,
        color_group="red",
        house_cost=150,
        rents=(18, 90, 250, 700, 875, 1050),
    ),
    MonopolySpace(22, "chance_2", "Chance", "chance"),
    MonopolySpace(
        23,
        "indiana_avenue",
        "Indiana Avenue",
        "property",
        220,
        18,
        color_group="red",
        house_cost=150,
        rents=(18, 90, 250, 700, 875, 1050),
    ),
    MonopolySpace(
        24,
        "illinois_avenue",
        "Illinois Avenue",
        "property",
        240,
        20,
        color_group="red",
        house_cost=150,
        rents=(20, 100, 300, 750, 925, 1100),
    ),
    MonopolySpace(25, "bo_railroad", "B. & O. Railroad", "railroad", 200, 25),
    MonopolySpace(
        26,
        "atlantic_avenue",
        "Atlantic Avenue",
        "property",
        260,
        22,
        color_group="yellow",
        house_cost=150,
        rents=(22, 110, 330, 800, 975, 1150),
    ),
    MonopolySpace(
        27,
        "ventnor_avenue",
        "Ventnor Avenue",
        "property",
        260,
        22,
        color_group="yellow",
        house_cost=150,
        rents=(22, 110, 330, 800, 975, 1150),
    ),
    MonopolySpace(28, "water_works", "Water Works", "utility", 150, 20),
    MonopolySpace(
        29,
        "marvin_gardens",
        "Marvin Gardens",
        "property",
        280,
        24,
        color_group="yellow",
        house_cost=150,
        rents=(24, 120, 360, 850, 1025, 1200),
    ),
    MonopolySpace(30, "go_to_jail", "Go to Jail", "go_to_jail"),
    MonopolySpace(
        31,
        "pacific_avenue",
        "Pacific Avenue",
        "property",
        300,
        26,
        color_group="green",
        house_cost=200,
        rents=(26, 130, 390, 900, 1100, 1275),
    ),
    MonopolySpace(
        32,
        "north_carolina_avenue",
        "North Carolina Avenue",
        "property",
        300,
        26,
        color_group="green",
        house_cost=200,
        rents=(26, 130, 390, 900, 1100, 1275),
    ),
    MonopolySpace(33, "community_chest_3", "Community Chest", "community_chest"),
    MonopolySpace(
        34,
        "pennsylvania_avenue",
        "Pennsylvania Avenue",
        "property",
        320,
        28,
        color_group="green",
        house_cost=200,
        rents=(28, 150, 450, 1000, 1200, 1400),
    ),
    MonopolySpace(35, "short_line", "Short Line", "railroad", 200, 25),
    MonopolySpace(36, "chance_3", "Chance", "chance"),
    MonopolySpace(
        37,
        "park_place",
        "Park Place",
        "property",
        350,
        35,
        color_group="dark_blue",
        house_cost=200,
        rents=(35, 175, 500, 1100, 1300, 1500),
    ),
    MonopolySpace(38, "luxury_tax", "Luxury Tax", "tax"),
    MonopolySpace(
        39,
        "boardwalk",
        "Boardwalk",
        "property",
        400,
        50,
        color_group="dark_blue",
        house_cost=200,
        rents=(50, 200, 600, 1400, 1700, 2000),
    ),
]
SPACE_BY_ID = {space.space_id: space for space in CLASSIC_STANDARD_BOARD}
COLOR_GROUP_TO_SPACE_IDS: dict[str, list[str]] = {}
for _space in CLASSIC_STANDARD_BOARD:
    if _space.color_group:
        COLOR_GROUP_TO_SPACE_IDS.setdefault(_space.color_group, []).append(_space.space_id)
PURCHASABLE_KINDS = {"property", "railroad", "utility"}
BOARD_SIZE = len(CLASSIC_STANDARD_BOARD)
STARTING_CASH = 1500
PASS_GO_CASH = 200
TAX_AMOUNTS = {"income_tax": 200, "luxury_tax": 100}
BAIL_AMOUNT = 50
MIN_AUCTION_INCREMENT = 10
TOTAL_HOUSES = 32
TOTAL_HOTELS = 12
JAIL_CARD_TRADE_CASH = 50

CHANCE_CARD_IDS = [
    "advance_to_go",
    "bank_dividend_50",
    "go_back_three",
    "go_to_jail",
    "poor_tax_15",
]
COMMUNITY_CHEST_CARD_IDS = [
    "bank_error_collect_200",
    "doctor_fee_pay_50",
    "income_tax_refund_20",
    "go_to_jail",
    "get_out_of_jail_free",
]
CARD_DESCRIPTION_KEYS = {
    "advance_to_go": "monopoly-card-advance-to-go",
    "bank_dividend_50": "monopoly-card-bank-dividend-50",
    "go_back_three": "monopoly-card-go-back-three",
    "go_to_jail": "monopoly-card-go-to-jail",
    "poor_tax_15": "monopoly-card-poor-tax-15",
    "bank_error_collect_200": "monopoly-card-bank-error-200",
    "doctor_fee_pay_50": "monopoly-card-doctor-fee-50",
    "income_tax_refund_20": "monopoly-card-tax-refund-20",
    "get_out_of_jail_free": "monopoly-card-get-out-of-jail",
}


@dataclass
class MonopolyPlayer(Player):
    """Player state for Monopoly scaffold."""

    position: int = 0
    cash: int = STARTING_CASH
    owned_space_ids: list[str] = field(default_factory=list)
    bankrupt: bool = False
    in_jail: bool = False
    jail_turns: int = 0
    get_out_of_jail_cards: int = 0


@dataclass
class MonopolyTradeOffer:
    """Pending trade offer between two players."""

    proposer_id: str = ""
    target_id: str = ""
    give_cash: int = 0
    give_property_id: str = ""
    give_jail_cards: int = 0
    receive_cash: int = 0
    receive_property_id: str = ""
    receive_jail_cards: int = 0
    summary: str = ""


@dataclass
class MonopolyOptions(GameOptions):
    """Lobby options for Monopoly scaffold."""

    preset_id: str = option_field(
        MenuOption(
            default=DEFAULT_PRESET_ID,
            choices=lambda game, player: game.get_available_preset_ids(),
            value_key="preset",
            choice_labels=PRESET_LABEL_KEYS,
            label="monopoly-set-preset",
            prompt="monopoly-select-preset",
            change_msg="monopoly-option-changed-preset",
        )
    )


@dataclass
@register_game
class MonopolyGame(ActionGuardMixin, Game):
    """Catalog-backed Monopoly scaffold.

    This class intentionally wires preset selection and metadata loading first.
    Gameplay mechanics are added incrementally in later milestones.
    """

    players: list[MonopolyPlayer] = field(default_factory=list)
    options: MonopolyOptions = field(default_factory=MonopolyOptions)

    active_preset_id: str = DEFAULT_PRESET_ID
    active_preset_name: str = ""
    active_family_key: str = ""
    active_edition_ids: list[str] = field(default_factory=list)
    active_anchor_edition_id: str = ""
    property_owners: dict[str, str] = field(default_factory=dict)
    mortgaged_space_ids: list[str] = field(default_factory=list)
    building_levels: dict[str, int] = field(default_factory=dict)
    pending_trade_offer: MonopolyTradeOffer | None = None

    turn_has_rolled: bool = False
    turn_last_roll: list[int] = field(default_factory=list)
    turn_pending_purchase_space_id: str = ""
    turn_doubles_count: int = 0
    turn_can_roll_again: bool = False

    chance_deck_order: list[str] = field(default_factory=lambda: CHANCE_CARD_IDS.copy())
    chance_deck_index: int = 0
    community_chest_deck_order: list[str] = field(
        default_factory=lambda: COMMUNITY_CHEST_CARD_IDS.copy()
    )
    community_chest_deck_index: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Monopoly"

    @classmethod
    def get_type(cls) -> str:
        return "monopoly"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> MonopolyPlayer:
        """Create a Monopoly player."""
        return MonopolyPlayer(id=player_id, name=name, is_bot=is_bot)

    def create_turn_action_set(self, player: MonopolyPlayer) -> ActionSet:
        """Create the turn action set for Monopoly."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "monopoly-roll-dice"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
            )
        )
        action_set.add(
            Action(
                id="buy_property",
                label=Localization.get(locale, "monopoly-buy-property"),
                handler="_action_buy_property",
                is_enabled="_is_buy_property_enabled",
                is_hidden="_is_buy_property_hidden",
            )
        )
        action_set.add(
            Action(
                id="auction_property",
                label=Localization.get(locale, "monopoly-auction-property"),
                handler="_action_auction_property",
                is_enabled="_is_auction_property_enabled",
                is_hidden="_is_auction_property_hidden",
            )
        )
        action_set.add(
            Action(
                id="mortgage_property",
                label=Localization.get(locale, "monopoly-mortgage-property"),
                handler="_action_mortgage_property",
                is_enabled="_is_mortgage_property_enabled",
                is_hidden="_is_mortgage_property_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-mortgage",
                    options="_options_for_mortgage_property",
                ),
            )
        )
        action_set.add(
            Action(
                id="unmortgage_property",
                label=Localization.get(locale, "monopoly-unmortgage-property"),
                handler="_action_unmortgage_property",
                is_enabled="_is_unmortgage_property_enabled",
                is_hidden="_is_unmortgage_property_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-unmortgage",
                    options="_options_for_unmortgage_property",
                ),
            )
        )
        action_set.add(
            Action(
                id="build_house",
                label=Localization.get(locale, "monopoly-build-house"),
                handler="_action_build_house",
                is_enabled="_is_build_house_enabled",
                is_hidden="_is_build_house_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-build",
                    options="_options_for_build_house",
                ),
            )
        )
        action_set.add(
            Action(
                id="sell_house",
                label=Localization.get(locale, "monopoly-sell-house"),
                handler="_action_sell_house",
                is_enabled="_is_sell_house_enabled",
                is_hidden="_is_sell_house_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-sell",
                    options="_options_for_sell_house",
                ),
            )
        )
        action_set.add(
            Action(
                id="offer_trade",
                label=Localization.get(locale, "monopoly-offer-trade"),
                handler="_action_offer_trade",
                is_enabled="_is_offer_trade_enabled",
                is_hidden="_is_offer_trade_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-trade-offer",
                    options="_options_for_offer_trade",
                ),
            )
        )
        action_set.add(
            Action(
                id="accept_trade",
                label=Localization.get(locale, "monopoly-accept-trade"),
                handler="_action_accept_trade",
                is_enabled="_is_accept_trade_enabled",
                is_hidden="_is_accept_trade_hidden",
            )
        )
        action_set.add(
            Action(
                id="decline_trade",
                label=Localization.get(locale, "monopoly-decline-trade"),
                handler="_action_decline_trade",
                is_enabled="_is_decline_trade_enabled",
                is_hidden="_is_decline_trade_hidden",
            )
        )
        action_set.add(
            Action(
                id="pay_bail",
                label=Localization.get(locale, "monopoly-pay-bail"),
                handler="_action_pay_bail",
                is_enabled="_is_pay_bail_enabled",
                is_hidden="_is_pay_bail_hidden",
            )
        )
        action_set.add(
            Action(
                id="use_jail_card",
                label=Localization.get(locale, "monopoly-use-jail-card"),
                handler="_action_use_jail_card",
                is_enabled="_is_use_jail_card_enabled",
                is_hidden="_is_use_jail_card_hidden",
            )
        )
        action_set.add(
            Action(
                id="end_turn",
                label=Localization.get(locale, "monopoly-end-turn"),
                handler="_action_end_turn",
                is_enabled="_is_end_turn_enabled",
                is_hidden="_is_end_turn_hidden",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        """Define keybinds for lobby + scaffold status checks."""
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll_dice"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Buy property", ["buy_property"], state=KeybindState.ACTIVE)
        self.define_keybind("a", "Auction property", ["auction_property"], state=KeybindState.ACTIVE)
        self.define_keybind("m", "Mortgage property", ["mortgage_property"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "shift+m",
            "Unmortgage property",
            ["unmortgage_property"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind("h", "Build house", ["build_house"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+h", "Sell house", ["sell_house"], state=KeybindState.ACTIVE)
        self.define_keybind("t", "Offer trade", ["offer_trade"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+t", "Accept trade", ["accept_trade"], state=KeybindState.ACTIVE)
        self.define_keybind("ctrl+t", "Decline trade", ["decline_trade"], state=KeybindState.ACTIVE)
        self.define_keybind("j", "Pay bail", ["pay_bail"], state=KeybindState.ACTIVE)
        self.define_keybind("e", "End turn", ["end_turn"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "p",
            "Announce current preset",
            ["announce_preset"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def create_standard_action_set(self, player: MonopolyPlayer) -> ActionSet:
        """Add preset announcement action to standard action set."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set.add(
            Action(
                id="announce_preset",
                label=Localization.get(locale, "monopoly-announce-preset"),
                handler="_action_announce_preset",
                is_enabled="_is_announce_preset_enabled",
                is_hidden="_is_announce_preset_hidden",
            )
        )
        return action_set

    def get_available_preset_ids(self) -> list[str]:
        """Return selectable preset ids from generated catalog artifacts."""
        return _catalog_preset_ids()

    def _fallback_preset(self) -> MonopolyPreset:
        """Return a safe fallback preset if artifacts are missing."""
        fallback_id = _catalog_default_preset_id()
        fallback = _catalog_get_preset(fallback_id)
        if fallback:
            return fallback
        return MonopolyPreset(
            preset_id=DEFAULT_PRESET_ID,
            family_key="classic_and_themed_standard",
            name="Classic and Themed Standard",
            description="Fallback preset when catalog artifacts are unavailable.",
            anchor_edition_id="",
            edition_ids=(),
        )

    def _resolve_selected_preset(self) -> MonopolyPreset:
        """Resolve currently selected lobby preset, applying fallback when needed."""
        selected = _catalog_get_preset(self.options.preset_id)
        if selected:
            return selected
        fallback = self._fallback_preset()
        self.options.preset_id = fallback.preset_id
        return fallback

    def _localize_preset_name(self, locale: str, preset_id: str, fallback: str) -> str:
        """Resolve localized preset label for speech."""
        preset_key = PRESET_LABEL_KEYS.get(preset_id)
        if not preset_key:
            return fallback
        text = Localization.get(locale, preset_key)
        if text == preset_key:
            return fallback
        return text

    def _is_announce_preset_enabled(self, player: Player) -> str | None:
        """Enable preset announcements during active play."""
        return self.guard_game_active()

    def _is_announce_preset_hidden(self, player: Player) -> Visibility:
        """Hide announce action from menus (keybind only)."""
        return Visibility.HIDDEN

    def _action_announce_preset(self, player: Player, action_id: str) -> None:
        """Speak current preset details to one player."""
        user = self.get_user(player)
        if not user:
            return
        preset_name = self._localize_preset_name(
            user.locale, self.active_preset_id, self.active_preset_name
        )
        user.speak_l(
            "monopoly-current-preset",
            preset=preset_name,
            count=len(self.active_edition_ids),
        )

    def _space_at(self, position: int) -> MonopolySpace:
        """Get board space by board index."""
        return CLASSIC_STANDARD_BOARD[position % BOARD_SIZE]

    def _space_label(self, space_id: str) -> str:
        """Return display label for a space id."""
        space = SPACE_BY_ID.get(space_id)
        return space.name if space else space_id

    def _mortgage_value(self, space: MonopolySpace) -> int:
        """Get mortgage value for a space."""
        return max(1, space.price // 2)

    def _unmortgage_cost(self, space: MonopolySpace) -> int:
        """Get unmortgage cost for a space."""
        mortgage_value = self._mortgage_value(space)
        return (mortgage_value * 11 + 9) // 10

    def _is_space_mortgaged(self, space_id: str) -> bool:
        """Check whether a space is currently mortgaged."""
        return space_id in self.mortgaged_space_ids

    def _building_level(self, space_id: str) -> int:
        """Get building level for a street property (0-5)."""
        return self.building_levels.get(space_id, 0)

    def _set_building_level(self, space_id: str, level: int) -> None:
        """Set building level for a street property (0-5)."""
        if space_id not in SPACE_BY_ID:
            return
        clamped = max(0, min(5, level))
        self.building_levels[space_id] = clamped

    def _is_street_property(self, space: MonopolySpace) -> bool:
        """Return True for color-group street properties."""
        return space.kind == "property" and bool(space.color_group)

    def _owner_has_full_color_set(self, owner_id: str, color_group: str) -> bool:
        """Check whether owner controls an entire color set."""
        group_ids = COLOR_GROUP_TO_SPACE_IDS.get(color_group, [])
        if not group_ids:
            return False
        return all(self.property_owners.get(space_id) == owner_id for space_id in group_ids)

    def _group_space_ids(self, color_group: str) -> list[str]:
        """Get all board space ids in one color group."""
        return COLOR_GROUP_TO_SPACE_IDS.get(color_group, [])

    def _group_levels(self, color_group: str) -> list[int]:
        """Get all building levels for one color group."""
        return [self._building_level(space_id) for space_id in self._group_space_ids(color_group)]

    def _group_has_mortgage(self, color_group: str) -> bool:
        """Return True if any property in the group is mortgaged."""
        return any(
            space_id in self.mortgaged_space_ids for space_id in self._group_space_ids(color_group)
        )

    def _group_has_any_buildings(self, color_group: str) -> bool:
        """Return True if any property in the group has buildings."""
        return any(self._building_level(space_id) > 0 for space_id in self._group_space_ids(color_group))

    def _building_supply_in_use(self) -> tuple[int, int]:
        """Return (houses_in_use, hotels_in_use) from board state."""
        houses = 0
        hotels = 0
        for level in self.building_levels.values():
            if level >= 5:
                hotels += 1
            else:
                houses += max(0, level)
        return houses, hotels

    def _available_houses(self) -> int:
        """Return houses currently available in bank supply."""
        houses_in_use, _ = self._building_supply_in_use()
        return max(0, TOTAL_HOUSES - houses_in_use)

    def _available_hotels(self) -> int:
        """Return hotels currently available in bank supply."""
        _, hotels_in_use = self._building_supply_in_use()
        return max(0, TOTAL_HOTELS - hotels_in_use)

    def _can_raise_building_level(self, space_id: str) -> bool:
        """Check supply constraints for +1 building level."""
        level = self._building_level(space_id)
        if level < 0 or level >= 5:
            return False
        if level <= 3:
            return self._available_houses() >= 1
        return self._available_hotels() >= 1

    def _can_lower_building_level(self, space_id: str) -> bool:
        """Check supply constraints for -1 building level."""
        level = self._building_level(space_id)
        if level <= 0:
            return False
        if level <= 4:
            return True
        return self._available_houses() >= 4

    def _pick_best_building_sale(self, space_ids: list[str]) -> str | None:
        """Pick the sale that usually raises cash fastest."""
        if not space_ids:
            return None
        ranked = sorted(
            space_ids,
            key=lambda space_id: (
                SPACE_BY_ID[space_id].house_cost,
                self._building_level(space_id),
                self._space_label(space_id),
            ),
            reverse=True,
        )
        return ranked[0]

    def _pick_best_mortgage(self, space_ids: list[str]) -> str | None:
        """Pick the mortgage that usually raises cash fastest."""
        if not space_ids:
            return None
        ranked = sorted(
            space_ids,
            key=lambda space_id: (
                self._mortgage_value(SPACE_BY_ID[space_id]),
                SPACE_BY_ID[space_id].price,
                self._space_label(space_id),
            ),
            reverse=True,
        )
        return ranked[0]

    def _liquidate_assets_for_debt(self, player: MonopolyPlayer, amount_due: int) -> None:
        """Auto-liquidate: sell buildings first, then mortgage, until debt is covered."""
        if amount_due <= 0 or player.cash >= amount_due:
            return

        attempts = 0
        max_attempts = max(8, len(player.owned_space_ids) * 8)
        while player.cash < amount_due and attempts < max_attempts:
            attempts += 1

            sell_choice = self._pick_best_building_sale(self._options_for_sell_house(player))
            if sell_choice:
                cash_before = player.cash
                self._action_sell_house(player, sell_choice, "sell_house")
                if player.cash > cash_before:
                    continue

            mortgage_choice = self._pick_best_mortgage(self._options_for_mortgage_property(player))
            if mortgage_choice:
                cash_before = player.cash
                self._action_mortgage_property(player, mortgage_choice, "mortgage_property")
                if player.cash > cash_before:
                    continue

            break

    def _property_trade_value(self, space_id: str) -> int:
        """Estimate trade value for a property."""
        space = SPACE_BY_ID.get(space_id)
        if not space:
            return 100
        return max(1, space.price)

    def _is_property_tradable_for_trade(self, space_id: str, owner_id: str) -> bool:
        """Return True when a property can be traded in a private deal."""
        if self.property_owners.get(space_id) != owner_id:
            return False
        space = SPACE_BY_ID.get(space_id)
        if not space or space.kind not in PURCHASABLE_KINDS:
            return False
        if self._is_street_property(space) and self._group_has_any_buildings(space.color_group):
            return False
        return True

    def _transfer_property(
        self,
        space_id: str,
        from_player: MonopolyPlayer,
        to_player: MonopolyPlayer,
    ) -> bool:
        """Transfer one property between players."""
        if not self._is_property_tradable_for_trade(space_id, from_player.id):
            return False
        self.property_owners[space_id] = to_player.id
        if space_id in from_player.owned_space_ids:
            from_player.owned_space_ids.remove(space_id)
        if space_id not in to_player.owned_space_ids:
            to_player.owned_space_ids.append(space_id)
        return True

    def _encode_trade_option(self, summary: str, offer: MonopolyTradeOffer) -> str:
        """Encode trade metadata into one menu option string."""
        return (
            f"{summary} ## target={offer.target_id};gc={offer.give_cash};"
            f"gp={offer.give_property_id or '-'};gj={offer.give_jail_cards};"
            f"rc={offer.receive_cash};rp={offer.receive_property_id or '-'};"
            f"rj={offer.receive_jail_cards}"
        )

    def _parse_trade_option(self, option: str) -> MonopolyTradeOffer | None:
        """Parse a trade option string from the menu."""
        if "##" not in option:
            return None
        summary, raw_meta = option.split("##", 1)
        meta: dict[str, str] = {}
        for part in raw_meta.strip().split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            meta[key.strip()] = value.strip()

        target_id = meta.get("target", "")
        if not target_id:
            return None
        try:
            give_cash = max(0, int(meta.get("gc", "0")))
            give_jail_cards = max(0, int(meta.get("gj", "0")))
            receive_cash = max(0, int(meta.get("rc", "0")))
            receive_jail_cards = max(0, int(meta.get("rj", "0")))
        except ValueError:
            return None

        give_property_id = meta.get("gp", "")
        if give_property_id == "-":
            give_property_id = ""
        receive_property_id = meta.get("rp", "")
        if receive_property_id == "-":
            receive_property_id = ""

        return MonopolyTradeOffer(
            target_id=target_id,
            give_cash=give_cash,
            give_property_id=give_property_id,
            give_jail_cards=give_jail_cards,
            receive_cash=receive_cash,
            receive_property_id=receive_property_id,
            receive_jail_cards=receive_jail_cards,
            summary=summary.strip(),
        )

    def _is_trade_offer_valid(
        self,
        proposer: MonopolyPlayer,
        target: MonopolyPlayer,
        offer: MonopolyTradeOffer,
    ) -> bool:
        """Validate that both sides can still perform an offered trade."""
        if proposer.bankrupt or target.bankrupt:
            return False
        if offer.target_id != target.id:
            return False
        if offer.give_cash < 0 or offer.receive_cash < 0:
            return False
        if offer.give_jail_cards < 0 or offer.receive_jail_cards < 0:
            return False

        proposer_gives_any = bool(
            offer.give_cash > 0 or offer.give_property_id or offer.give_jail_cards > 0
        )
        proposer_gets_any = bool(
            offer.receive_cash > 0 or offer.receive_property_id or offer.receive_jail_cards > 0
        )
        if not proposer_gives_any or not proposer_gets_any:
            return False

        if proposer.cash < offer.give_cash:
            return False
        if target.cash < offer.receive_cash:
            return False
        if proposer.get_out_of_jail_cards < offer.give_jail_cards:
            return False
        if target.get_out_of_jail_cards < offer.receive_jail_cards:
            return False

        if offer.give_property_id and not self._is_property_tradable_for_trade(
            offer.give_property_id, proposer.id
        ):
            return False
        if offer.receive_property_id and not self._is_property_tradable_for_trade(
            offer.receive_property_id, target.id
        ):
            return False
        return True

    def _apply_trade_offer(
        self,
        proposer: MonopolyPlayer,
        target: MonopolyPlayer,
        offer: MonopolyTradeOffer,
    ) -> bool:
        """Apply a validated trade offer."""
        if not self._is_trade_offer_valid(proposer, target, offer):
            return False

        if offer.give_property_id and not self._transfer_property(offer.give_property_id, proposer, target):
            return False
        if offer.receive_property_id and not self._transfer_property(
            offer.receive_property_id, target, proposer
        ):
            return False

        proposer.cash -= offer.give_cash
        target.cash += offer.give_cash

        target.cash -= offer.receive_cash
        proposer.cash += offer.receive_cash

        proposer.get_out_of_jail_cards -= offer.give_jail_cards
        target.get_out_of_jail_cards += offer.give_jail_cards

        target.get_out_of_jail_cards -= offer.receive_jail_cards
        proposer.get_out_of_jail_cards += offer.receive_jail_cards
        return True

    def _bot_accepts_trade_offer(
        self,
        proposer: MonopolyPlayer,
        target: MonopolyPlayer,
        offer: MonopolyTradeOffer,
    ) -> bool:
        """Simple heuristic for bot trade acceptance."""
        if not self._is_trade_offer_valid(proposer, target, offer):
            return False

        target_gain = (
            offer.give_cash
            + (self._property_trade_value(offer.give_property_id) if offer.give_property_id else 0)
            + (offer.give_jail_cards * JAIL_CARD_TRADE_CASH)
        )
        target_cost = (
            offer.receive_cash
            + (self._property_trade_value(offer.receive_property_id) if offer.receive_property_id else 0)
            + (offer.receive_jail_cards * JAIL_CARD_TRADE_CASH)
        )
        return target_gain >= target_cost

    def _pending_trade_for_target(self, player: MonopolyPlayer) -> MonopolyTradeOffer | None:
        """Return pending trade offer when player is the offer target."""
        offer = self.pending_trade_offer
        if not offer or offer.target_id != player.id:
            return None
        return offer

    def _pending_trade_for_proposer(self, player: MonopolyPlayer) -> MonopolyTradeOffer | None:
        """Return pending trade offer when player is the offer proposer."""
        offer = self.pending_trade_offer
        if not offer or offer.proposer_id != player.id:
            return None
        return offer

    def _options_for_offer_trade(self, player: Player) -> list[str]:
        """Menu options for private trades from current player to others."""
        mono_player: MonopolyPlayer = player  # type: ignore
        options: list[str] = []
        other_players = [
            p
            for p in self.turn_players
            if isinstance(p, MonopolyPlayer) and p.id != mono_player.id and not p.bankrupt
        ]
        for other in other_players:
            # Buy one tradable property from target for listed price.
            for space_id in sorted(other.owned_space_ids):
                if not self._is_property_tradable_for_trade(space_id, other.id):
                    continue
                price = self._property_trade_value(space_id)
                if mono_player.cash < price:
                    continue
                summary = f"Buy {self._space_label(space_id)} from {other.name} for {price}"
                offer = MonopolyTradeOffer(
                    target_id=other.id,
                    give_cash=price,
                    receive_property_id=space_id,
                    summary=summary,
                )
                options.append(self._encode_trade_option(summary, offer))

            # Sell one tradable property to target for listed price.
            for space_id in sorted(mono_player.owned_space_ids):
                if not self._is_property_tradable_for_trade(space_id, mono_player.id):
                    continue
                price = self._property_trade_value(space_id)
                if other.cash < price:
                    continue
                summary = f"Sell {self._space_label(space_id)} to {other.name} for {price}"
                offer = MonopolyTradeOffer(
                    target_id=other.id,
                    give_property_id=space_id,
                    receive_cash=price,
                    summary=summary,
                )
                options.append(self._encode_trade_option(summary, offer))

            # Jail-card for cash offers.
            if other.get_out_of_jail_cards > 0 and mono_player.cash >= JAIL_CARD_TRADE_CASH:
                summary = f"Buy jail card from {other.name} for {JAIL_CARD_TRADE_CASH}"
                offer = MonopolyTradeOffer(
                    target_id=other.id,
                    give_cash=JAIL_CARD_TRADE_CASH,
                    receive_jail_cards=1,
                    summary=summary,
                )
                options.append(self._encode_trade_option(summary, offer))
            if mono_player.get_out_of_jail_cards > 0 and other.cash >= JAIL_CARD_TRADE_CASH:
                summary = f"Sell jail card to {other.name} for {JAIL_CARD_TRADE_CASH}"
                offer = MonopolyTradeOffer(
                    target_id=other.id,
                    give_jail_cards=1,
                    receive_cash=JAIL_CARD_TRADE_CASH,
                    summary=summary,
                )
                options.append(self._encode_trade_option(summary, offer))

        # Keep list stable and reasonably sized for menu navigation.
        deduped = sorted(dict.fromkeys(options))
        return deduped[:120]

    def _count_owned_kind(self, owner_id: str, kind: str) -> int:
        """Count how many properties of a kind the owner controls."""
        total = 0
        for space_id, space_owner_id in self.property_owners.items():
            if space_owner_id != owner_id:
                continue
            space = SPACE_BY_ID.get(space_id)
            if space and space.kind == kind:
                total += 1
        return total

    def _calculate_rent_due(
        self, space: MonopolySpace, owner_id: str, dice_total: int | None
    ) -> int:
        """Compute official-ish rent for a landed space."""
        if self._is_street_property(space):
            level = self._building_level(space.space_id)
            if space.rents:
                if level > 0:
                    return space.rents[min(level, len(space.rents) - 1)]
                base = space.rents[0]
            else:
                base = space.rent
            if self._owner_has_full_color_set(owner_id, space.color_group):
                return base * 2
            return base

        if space.kind == "railroad":
            owned = max(1, self._count_owned_kind(owner_id, "railroad"))
            return 25 * (2 ** (owned - 1))

        if space.kind == "utility":
            owned = max(1, self._count_owned_kind(owner_id, "utility"))
            factor = 10 if owned >= 2 else 4
            roll_value = dice_total if dice_total is not None else sum(self.turn_last_roll)
            return factor * max(0, roll_value)

        return space.rent

    def _pending_purchase_space(self) -> MonopolySpace | None:
        """Get the currently pending purchasable space for this turn."""
        if not self.turn_pending_purchase_space_id:
            return None
        return SPACE_BY_ID.get(self.turn_pending_purchase_space_id)

    def _can_buy_pending_space(self, player: MonopolyPlayer) -> bool:
        """Return True if the active player can buy pending space now."""
        space = self._pending_purchase_space()
        if not space:
            return False
        if space.kind not in PURCHASABLE_KINDS:
            return False
        if space.space_id in self.property_owners:
            return False
        return player.cash >= space.price > 0

    def _reset_turn_state(self, *, reset_doubles: bool = True) -> None:
        """Reset transient per-turn state."""
        self.turn_has_rolled = False
        self.turn_last_roll.clear()
        self.turn_pending_purchase_space_id = ""
        self.turn_can_roll_again = False
        if reset_doubles:
            self.turn_doubles_count = 0

    def _prepare_next_roll_after_doubles(self, player: MonopolyPlayer) -> None:
        """Unlock another roll for doubles chain turns."""
        self.turn_has_rolled = False
        self.turn_last_roll.clear()
        self.turn_pending_purchase_space_id = ""
        self.turn_can_roll_again = False
        self.broadcast_l("monopoly-roll-again", player=player.name)

    def _move_player(
        self, player: MonopolyPlayer, steps: int, *, collect_pass_go: bool
    ) -> MonopolySpace:
        """Move player by steps and return landed space."""
        old_position = player.position
        absolute_position = old_position + steps
        player.position = absolute_position % BOARD_SIZE

        if collect_pass_go and absolute_position >= BOARD_SIZE:
            player.cash += PASS_GO_CASH
            self.broadcast_l(
                "monopoly-pass-go",
                player=player.name,
                amount=PASS_GO_CASH,
                cash=player.cash,
            )
        return self._space_at(player.position)

    def _draw_card(self, deck_type: str) -> str:
        """Draw the next card from a deck in cyclic order."""
        if deck_type == "chance":
            if not self.chance_deck_order:
                self.chance_deck_order = CHANCE_CARD_IDS.copy()
                random.shuffle(self.chance_deck_order)
            card = self.chance_deck_order[self.chance_deck_index % len(self.chance_deck_order)]
            self.chance_deck_index += 1
            return card

        if not self.community_chest_deck_order:
            self.community_chest_deck_order = COMMUNITY_CHEST_CARD_IDS.copy()
            random.shuffle(self.community_chest_deck_order)
        card = self.community_chest_deck_order[
            self.community_chest_deck_index % len(self.community_chest_deck_order)
        ]
        self.community_chest_deck_index += 1
        return card

    def _send_to_jail(self, player: MonopolyPlayer, *, by_triple_doubles: bool = False) -> None:
        """Send a player to jail and clear unresolved landing state."""
        player.position = 10
        player.in_jail = True
        player.jail_turns = 0
        self.turn_pending_purchase_space_id = ""
        self.turn_can_roll_again = False

        if by_triple_doubles:
            self.broadcast_l("monopoly-three-doubles-jail", player=player.name)
        else:
            jail_space = self._space_at(10)
            self.broadcast_l(
                "monopoly-go-to-jail",
                player=player.name,
                space=jail_space.name,
            )

    def _apply_bank_payment(
        self,
        player: MonopolyPlayer,
        amount: int,
        *,
        tax_name: str | None = None,
        card_reason_key: str | None = None,
    ) -> bool:
        """Charge player money to bank; return False if player bankrupt."""
        if player.cash < amount:
            self._liquidate_assets_for_debt(player, amount)

        paid = min(player.cash, amount)
        player.cash -= paid

        if tax_name:
            self.broadcast_l(
                "monopoly-tax-paid",
                player=player.name,
                amount=paid,
                tax=tax_name,
                cash=player.cash,
            )
        elif card_reason_key:
            self.broadcast_l(
                card_reason_key,
                player=player.name,
                amount=paid,
                cash=player.cash,
            )

        if paid < amount:
            self._declare_bankrupt(player)
            return False
        return True

    def _sync_cash_scores(self) -> None:
        """Mirror player cash into team scores for score actions."""
        if self._team_manager.team_mode != "individual":
            return
        for team in self._team_manager.teams:
            if not team.members:
                continue
            player = self.get_player_by_name(team.members[0])
            team.total_score = player.cash if player else 0
            team.round_score = 0

    def _declare_bankrupt(
        self,
        player: MonopolyPlayer,
        *,
        creditor_name: str | None = None,
        creditor_id: str | None = None,
    ) -> None:
        """Mark a player bankrupt, release their holdings, and check winner."""
        if player.bankrupt:
            return

        player.bankrupt = True
        creditor: MonopolyPlayer | None = None
        if creditor_id:
            maybe_creditor = self.get_player_by_id(creditor_id)
            if (
                maybe_creditor
                and isinstance(maybe_creditor, MonopolyPlayer)
                and not maybe_creditor.bankrupt
                and maybe_creditor.id != player.id
            ):
                creditor = maybe_creditor

        for space_id in list(player.owned_space_ids):
            if self.property_owners.get(space_id) == player.id:
                if creditor:
                    self.property_owners[space_id] = creditor.id
                    if space_id not in creditor.owned_space_ids:
                        creditor.owned_space_ids.append(space_id)
                else:
                    del self.property_owners[space_id]
            if not creditor and space_id in self.mortgaged_space_ids:
                self.mortgaged_space_ids.remove(space_id)
            # Buildings are liquidated during bankruptcy transfer/release.
            if space_id in self.building_levels:
                self.building_levels[space_id] = 0
        if creditor and player.get_out_of_jail_cards > 0:
            creditor.get_out_of_jail_cards += player.get_out_of_jail_cards
        player.get_out_of_jail_cards = 0
        player.cash = 0
        player.owned_space_ids.clear()
        player.in_jail = False
        player.jail_turns = 0

        pending = self.pending_trade_offer
        if pending and (pending.proposer_id == player.id or pending.target_id == player.id):
            self.broadcast_l("monopoly-trade-cancelled", offer=pending.summary)
            self.pending_trade_offer = None

        self.broadcast_l(
            "monopoly-player-bankrupt",
            player=player.name,
            creditor=creditor_name or (creditor.name if creditor else "Bank"),
        )

        ordered_before = self.turn_players
        try:
            old_index = ordered_before.index(player)
        except ValueError:
            old_index = 0

        remaining = [turn_player for turn_player in ordered_before if not turn_player.bankrupt]
        if len(remaining) <= 1:
            self.status = "finished"
            self.game_active = False
            self.set_turn_players(remaining)
            if remaining:
                winner = remaining[0]
                self.broadcast_l(
                    "monopoly-winner-by-bankruptcy",
                    player=winner.name,
                    cash=winner.cash,
                )
            return

        self.set_turn_players(remaining, reset_index=False)
        self.turn_index = old_index % len(remaining)
        self._reset_turn_state()
        self.announce_turn(turn_sound="game_pig/turn.ogg")
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(8, 14))

    def _resolve_card_effect(
        self,
        player: MonopolyPlayer,
        deck_type: str,
        card_id: str,
        *,
        depth: int,
        dice_total: int | None,
    ) -> str:
        """Apply one Chance/Community Chest card and return resolution state."""
        deck_label = "Chance" if deck_type == "chance" else "Community Chest"
        card_text_key = CARD_DESCRIPTION_KEYS.get(card_id, card_id)
        card_text = Localization.get("en", card_text_key)
        self.broadcast_l(
            "monopoly-card-drawn",
            player=player.name,
            deck=deck_label,
            card=card_text,
        )

        if card_id == "advance_to_go":
            player.position = 0
            player.cash += PASS_GO_CASH
            self.broadcast_l(
                "monopoly-pass-go",
                player=player.name,
                amount=PASS_GO_CASH,
                cash=player.cash,
            )
            return "resolved"

        if card_id == "bank_dividend_50":
            player.cash += 50
            self.broadcast_l("monopoly-card-collect", player=player.name, amount=50, cash=player.cash)
            return "resolved"

        if card_id == "go_back_three":
            player.position = (player.position - 3) % BOARD_SIZE
            landed_space = self._space_at(player.position)
            self.broadcast_l(
                "monopoly-card-move",
                player=player.name,
                space=landed_space.name,
            )
            return self._resolve_space(
                player, landed_space, depth=depth + 1, dice_total=dice_total
            )

        if card_id == "go_to_jail":
            self._send_to_jail(player)
            return "forced_end"

        if card_id == "poor_tax_15":
            if not self._apply_bank_payment(
                player,
                15,
                card_reason_key="monopoly-card-pay",
            ):
                return "bankrupt"
            return "resolved"

        if card_id == "bank_error_collect_200":
            player.cash += 200
            self.broadcast_l(
                "monopoly-card-collect",
                player=player.name,
                amount=200,
                cash=player.cash,
            )
            return "resolved"

        if card_id == "doctor_fee_pay_50":
            if not self._apply_bank_payment(
                player,
                50,
                card_reason_key="monopoly-card-pay",
            ):
                return "bankrupt"
            return "resolved"

        if card_id == "income_tax_refund_20":
            player.cash += 20
            self.broadcast_l(
                "monopoly-card-collect",
                player=player.name,
                amount=20,
                cash=player.cash,
            )
            return "resolved"

        if card_id == "get_out_of_jail_free":
            player.get_out_of_jail_cards += 1
            self.broadcast_l(
                "monopoly-card-jail-free",
                player=player.name,
                cards=player.get_out_of_jail_cards,
            )
            return "resolved"

        return "resolved"

    def _resolve_space(
        self,
        player: MonopolyPlayer,
        landed_space: MonopolySpace,
        *,
        depth: int = 0,
        dice_total: int | None = None,
    ) -> str:
        """Resolve effects for the landed space.

        Returns:
            "pending_purchase" when buy/auction decision is required,
            "forced_end" when player was sent to jail,
            "bankrupt" when player went bankrupt,
            "resolved" otherwise.
        """
        if depth > 4:
            return "resolved"

        if landed_space.kind in PURCHASABLE_KINDS:
            owner_id = self.property_owners.get(landed_space.space_id)
            if owner_id is None:
                self.turn_pending_purchase_space_id = landed_space.space_id
                self.broadcast_l(
                    "monopoly-property-available",
                    player=player.name,
                    property=landed_space.name,
                    price=landed_space.price,
                )
                return "pending_purchase"

            if owner_id == player.id:
                self.broadcast_l(
                    "monopoly-landed-owned",
                    player=player.name,
                    property=landed_space.name,
                )
                return "resolved"

            if self._is_space_mortgaged(landed_space.space_id):
                self.broadcast_l(
                    "monopoly-mortgaged-no-rent",
                    player=player.name,
                    property=landed_space.name,
                )
                return "resolved"

            owner = self.get_player_by_id(owner_id)
            rent_due = self._calculate_rent_due(landed_space, owner_id, dice_total)
            if player.cash < rent_due:
                self._liquidate_assets_for_debt(player, rent_due)
            paid = min(player.cash, rent_due)
            player.cash -= paid
            if owner and isinstance(owner, MonopolyPlayer):
                owner.cash += paid

            self.broadcast_l(
                "monopoly-rent-paid",
                player=player.name,
                owner=owner.name if owner else "Bank",
                amount=paid,
                property=landed_space.name,
            )
            if paid < rent_due:
                creditor_name = owner.name if owner else "Bank"
                creditor_id = owner.id if owner and isinstance(owner, MonopolyPlayer) else None
                self._declare_bankrupt(
                    player,
                    creditor_name=creditor_name,
                    creditor_id=creditor_id,
                )
                return "bankrupt"
            return "resolved"

        if landed_space.space_id in TAX_AMOUNTS:
            if not self._apply_bank_payment(
                player,
                TAX_AMOUNTS[landed_space.space_id],
                tax_name=landed_space.name,
            ):
                return "bankrupt"
            return "resolved"

        if landed_space.kind == "go_to_jail":
            self._send_to_jail(player)
            return "forced_end"

        if landed_space.kind == "chance":
            card = self._draw_card("chance")
            return self._resolve_card_effect(
                player,
                "chance",
                card,
                depth=depth,
                dice_total=dice_total,
            )

        if landed_space.kind == "community_chest":
            card = self._draw_card("community_chest")
            return self._resolve_card_effect(
                player,
                "community_chest",
                card,
                depth=depth,
                dice_total=dice_total,
            )

        return "resolved"

    def _run_property_auction(self, space: MonopolySpace, declined_by: MonopolyPlayer) -> None:
        """Run a simple automatic auction for an unpurchased space."""
        bidders: list[tuple[MonopolyPlayer, int]] = []
        order = [p for p in self.turn_players if isinstance(p, MonopolyPlayer)]
        for bidder in order:
            if bidder.bankrupt:
                continue
            weight = 0.75 if bidder.id == declined_by.id else 0.9
            max_bid = min(space.price, int(bidder.cash * weight))
            if max_bid >= MIN_AUCTION_INCREMENT:
                bidders.append((bidder, max_bid))

        if not bidders:
            self.broadcast_l("monopoly-auction-no-bids", property=space.name)
            return

        bidders.sort(key=lambda row: row[1], reverse=True)
        winner, winner_cap = bidders[0]
        second_cap = bidders[1][1] if len(bidders) > 1 else 0
        reserve = max(1, space.price // 2)
        if len(bidders) == 1:
            winning_bid = min(winner_cap, reserve)
        else:
            winning_bid = min(winner_cap, second_cap + MIN_AUCTION_INCREMENT)
        winning_bid = max(1, winning_bid)

        winner.cash -= winning_bid
        if space.space_id not in winner.owned_space_ids:
            winner.owned_space_ids.append(space.space_id)
        self.property_owners[space.space_id] = winner.id
        if space.space_id in self.mortgaged_space_ids:
            self.mortgaged_space_ids.remove(space.space_id)

        self.broadcast_l(
            "monopoly-auction-won",
            player=winner.name,
            property=space.name,
            amount=winning_bid,
            cash=winner.cash,
        )

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        """Enable roll action for active player before rolling."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        if self.turn_has_rolled:
            return "monopoly-already-rolled"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        """Hide roll once a roll has been made this turn."""
        return self.turn_action_visibility(
            player,
            extra_condition=not self.turn_has_rolled and not self.turn_pending_purchase_space_id,
        )

    def _is_buy_property_enabled(self, player: Player) -> str | None:
        """Enable buy action when current player can buy landed property."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if not self.turn_has_rolled:
            return "monopoly-roll-first"
        mono_player: MonopolyPlayer = player  # type: ignore
        space = self._pending_purchase_space()
        if not space:
            return "monopoly-no-property-to-buy"
        if space.space_id in self.property_owners:
            return "monopoly-property-owned"
        if mono_player.cash < space.price:
            return "monopoly-not-enough-cash"
        return None

    def _is_buy_property_hidden(self, player: Player) -> Visibility:
        """Show buy action only after a roll when a property is pending."""
        return self.turn_action_visibility(
            player,
            extra_condition=self.turn_has_rolled and self._pending_purchase_space() is not None,
        )

    def _is_auction_property_enabled(self, player: Player) -> str | None:
        """Enable auction action for pending unpurchased property."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if not self.turn_has_rolled:
            return "monopoly-roll-first"
        if self._pending_purchase_space() is None:
            return "monopoly-no-property-to-auction"
        return None

    def _is_auction_property_hidden(self, player: Player) -> Visibility:
        """Show auction only when property purchase is pending."""
        return self.turn_action_visibility(
            player,
            extra_condition=self.turn_has_rolled and self._pending_purchase_space() is not None,
        )

    def _options_for_mortgage_property(self, player: Player) -> list[str]:
        """Menu options for unmortgaged owned properties."""
        mono_player: MonopolyPlayer = player  # type: ignore
        options: list[str] = []
        for space_id in mono_player.owned_space_ids:
            if self.property_owners.get(space_id) != mono_player.id:
                continue
            if space_id in self.mortgaged_space_ids:
                continue
            space = SPACE_BY_ID.get(space_id)
            if not space:
                continue
            if self._is_street_property(space) and self._group_has_any_buildings(space.color_group):
                continue
            options.append(space_id)
        return sorted(options)

    def _options_for_unmortgage_property(self, player: Player) -> list[str]:
        """Menu options for mortgaged owned properties."""
        mono_player: MonopolyPlayer = player  # type: ignore
        return sorted(
            [
                space_id
                for space_id in mono_player.owned_space_ids
                if self.property_owners.get(space_id) == mono_player.id
                and space_id in self.mortgaged_space_ids
            ]
        )

    def _options_for_build_house(self, player: Player) -> list[str]:
        """Menu options for buildable street properties."""
        mono_player: MonopolyPlayer = player  # type: ignore
        options: list[str] = []
        for space_id in mono_player.owned_space_ids:
            if self.property_owners.get(space_id) != mono_player.id:
                continue
            space = SPACE_BY_ID.get(space_id)
            if not space or not self._is_street_property(space):
                continue
            if space_id in self.mortgaged_space_ids:
                continue
            if not self._owner_has_full_color_set(mono_player.id, space.color_group):
                continue
            if self._group_has_mortgage(space.color_group):
                continue
            level = self._building_level(space_id)
            if level >= 5:
                continue
            if not self._can_raise_building_level(space_id):
                continue
            levels = self._group_levels(space.color_group)
            if not levels or level != min(levels):
                continue
            if mono_player.cash < space.house_cost:
                continue
            options.append(space_id)
        return sorted(options)

    def _options_for_sell_house(self, player: Player) -> list[str]:
        """Menu options for sellable street properties."""
        mono_player: MonopolyPlayer = player  # type: ignore
        options: list[str] = []
        for space_id in mono_player.owned_space_ids:
            if self.property_owners.get(space_id) != mono_player.id:
                continue
            space = SPACE_BY_ID.get(space_id)
            if not space or not self._is_street_property(space):
                continue
            level = self._building_level(space_id)
            if level <= 0:
                continue
            if not self._can_lower_building_level(space_id):
                continue
            levels = self._group_levels(space.color_group)
            if not levels or level != max(levels):
                continue
            options.append(space_id)
        return sorted(options)

    def _is_mortgage_property_enabled(self, player: Player) -> str | None:
        """Enable mortgage action when player owns eligible properties."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if not self._options_for_mortgage_property(player):
            return "monopoly-no-mortgage-options"
        return None

    def _is_mortgage_property_hidden(self, player: Player) -> Visibility:
        """Show mortgage action when options exist."""
        return self.turn_action_visibility(
            player, extra_condition=bool(self._options_for_mortgage_property(player))
        )

    def _is_unmortgage_property_enabled(self, player: Player) -> str | None:
        """Enable unmortgage action when player has mortgaged properties."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if not self._options_for_unmortgage_property(player):
            return "monopoly-no-unmortgage-options"
        return None

    def _is_unmortgage_property_hidden(self, player: Player) -> Visibility:
        """Show unmortgage action only when options exist."""
        return self.turn_action_visibility(
            player, extra_condition=bool(self._options_for_unmortgage_property(player))
        )

    def _is_build_house_enabled(self, player: Player) -> str | None:
        """Enable house-building when at least one valid build exists."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if not self._options_for_build_house(player):
            return "monopoly-no-build-options"
        return None

    def _is_build_house_hidden(self, player: Player) -> Visibility:
        """Show build action when options exist."""
        return self.turn_action_visibility(
            player, extra_condition=bool(self._options_for_build_house(player))
        )

    def _is_sell_house_enabled(self, player: Player) -> str | None:
        """Enable house selling when at least one valid sell exists."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if not self._options_for_sell_house(player):
            return "monopoly-no-sell-options"
        return None

    def _is_sell_house_hidden(self, player: Player) -> Visibility:
        """Show sell action when options exist."""
        return self.turn_action_visibility(
            player, extra_condition=bool(self._options_for_sell_house(player))
        )

    def _is_offer_trade_enabled(self, player: Player) -> str | None:
        """Enable trade offers for active players with at least one valid option."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        if self.pending_trade_offer is not None:
            return "monopoly-trade-pending"
        if not self._options_for_offer_trade(player):
            return "monopoly-no-trade-options"
        return None

    def _is_offer_trade_hidden(self, player: Player) -> Visibility:
        """Show offer-trade when player can open a new trade."""
        return self.turn_action_visibility(
            player,
            extra_condition=self.pending_trade_offer is None and bool(self._options_for_offer_trade(player)),
        )

    def _is_accept_trade_enabled(self, player: Player) -> str | None:
        """Enable accepting a pending trade for the addressed target player."""
        error = self.guard_turn_action_enabled(player, require_current_player=False)
        if error:
            return error
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if self._pending_trade_for_target(mono_player) is None:
            return "monopoly-no-trade-pending"
        return None

    def _is_accept_trade_hidden(self, player: Player) -> Visibility:
        """Show accept-trade only to the targeted player."""
        mono_player: MonopolyPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            require_current_player=False,
            extra_condition=self._pending_trade_for_target(mono_player) is not None,
        )

    def _is_decline_trade_enabled(self, player: Player) -> str | None:
        """Enable declining a pending trade for the addressed target player."""
        error = self.guard_turn_action_enabled(player, require_current_player=False)
        if error:
            return error
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        mono_player: MonopolyPlayer = player  # type: ignore
        if mono_player.bankrupt:
            return "monopoly-bankrupt-player"
        if self._pending_trade_for_target(mono_player) is None:
            return "monopoly-no-trade-pending"
        return None

    def _is_decline_trade_hidden(self, player: Player) -> Visibility:
        """Show decline-trade only to the targeted player."""
        mono_player: MonopolyPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            require_current_player=False,
            extra_condition=self._pending_trade_for_target(mono_player) is not None,
        )

    def _is_pay_bail_enabled(self, player: Player) -> str | None:
        """Enable paying bail while in jail before rolling."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if not mono_player.in_jail:
            return "monopoly-not-in-jail"
        if self.turn_has_rolled:
            return "monopoly-already-rolled"
        if mono_player.cash < BAIL_AMOUNT:
            return "monopoly-not-enough-cash"
        return None

    def _is_pay_bail_hidden(self, player: Player) -> Visibility:
        """Show pay bail only while player is jailed and has not rolled."""
        mono_player: MonopolyPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            extra_condition=mono_player.in_jail and not self.turn_has_rolled,
        )

    def _is_use_jail_card_enabled(self, player: Player) -> str | None:
        """Enable jail-card use while in jail before rolling."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        mono_player: MonopolyPlayer = player  # type: ignore
        if not mono_player.in_jail:
            return "monopoly-not-in-jail"
        if self.turn_has_rolled:
            return "monopoly-already-rolled"
        if mono_player.get_out_of_jail_cards <= 0:
            return "monopoly-no-jail-card"
        return None

    def _is_use_jail_card_hidden(self, player: Player) -> Visibility:
        """Show jail-card action only while usable."""
        mono_player: MonopolyPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            extra_condition=mono_player.in_jail
            and not self.turn_has_rolled
            and mono_player.get_out_of_jail_cards > 0,
        )

    def _is_end_turn_enabled(self, player: Player) -> str | None:
        """Enable end-turn after rolling."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if not self.turn_has_rolled:
            return "monopoly-roll-first"
        if self.turn_pending_purchase_space_id:
            return "monopoly-resolve-property-first"
        if self.turn_can_roll_again:
            return "monopoly-roll-again-required"
        return None

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        """Hide end-turn until player has rolled."""
        return self.turn_action_visibility(
            player,
            extra_condition=self.turn_has_rolled
            and not self.turn_pending_purchase_space_id
            and not self.turn_can_roll_again,
        )

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        """Handle rolling and landing logic for classic scaffold."""
        mono_player: MonopolyPlayer = player  # type: ignore

        if self.turn_has_rolled or mono_player.bankrupt or self.turn_pending_purchase_space_id:
            return

        die_1 = random.randint(1, 6)
        die_2 = random.randint(1, 6)
        total = die_1 + die_2
        is_doubles = die_1 == die_2

        self.turn_has_rolled = True
        self.turn_last_roll = [die_1, die_2]
        self.turn_pending_purchase_space_id = ""
        if mono_player.in_jail:
            if is_doubles:
                mono_player.in_jail = False
                mono_player.jail_turns = 0
                self.broadcast_l(
                    "monopoly-jail-roll-doubles",
                    player=mono_player.name,
                    die1=die_1,
                    die2=die_2,
                )
                landed_space = self._move_player(
                    mono_player, total, collect_pass_go=False
                )
                self.broadcast_l(
                    "monopoly-roll-result",
                    player=mono_player.name,
                    die1=die_1,
                    die2=die_2,
                    total=total,
                    space=landed_space.name,
                )
                self._resolve_space(mono_player, landed_space, dice_total=total)
            else:
                mono_player.jail_turns += 1
                self.broadcast_l(
                    "monopoly-jail-roll-failed",
                    player=mono_player.name,
                    die1=die_1,
                    die2=die_2,
                    attempts=mono_player.jail_turns,
                )
                if mono_player.jail_turns >= 3:
                    if mono_player.cash < BAIL_AMOUNT:
                        self._liquidate_assets_for_debt(mono_player, BAIL_AMOUNT)
                    if mono_player.cash < BAIL_AMOUNT:
                        self._declare_bankrupt(mono_player)
                        self._sync_cash_scores()
                        self.rebuild_all_menus()
                        return
                    mono_player.cash -= BAIL_AMOUNT
                    mono_player.in_jail = False
                    mono_player.jail_turns = 0
                    self.broadcast_l(
                        "monopoly-bail-paid",
                        player=mono_player.name,
                        amount=BAIL_AMOUNT,
                        cash=mono_player.cash,
                    )
                    landed_space = self._move_player(
                        mono_player, total, collect_pass_go=False
                    )
                    self.broadcast_l(
                        "monopoly-roll-result",
                        player=mono_player.name,
                        die1=die_1,
                        die2=die_2,
                        total=total,
                        space=landed_space.name,
                    )
                    self._resolve_space(mono_player, landed_space, dice_total=total)
            self.turn_doubles_count = 0
            self._sync_cash_scores()
            self.rebuild_all_menus()
            return

        if is_doubles:
            self.turn_doubles_count += 1
        else:
            self.turn_doubles_count = 0

        if self.turn_doubles_count >= 3:
            self._send_to_jail(mono_player, by_triple_doubles=True)
            self._sync_cash_scores()
            self.rebuild_all_menus()
            return

        landed_space = self._move_player(mono_player, total, collect_pass_go=True)
        self.broadcast_l(
            "monopoly-roll-result",
            player=mono_player.name,
            die1=die_1,
            die2=die_2,
            total=total,
            space=landed_space.name,
        )
        resolution = self._resolve_space(mono_player, landed_space, dice_total=total)

        if not mono_player.bankrupt and resolution == "resolved" and is_doubles:
            self._prepare_next_roll_after_doubles(mono_player)
        elif not mono_player.bankrupt and resolution == "pending_purchase" and is_doubles:
            self.turn_can_roll_again = True

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_buy_property(self, player: Player, action_id: str) -> None:
        """Buy currently pending property."""
        mono_player: MonopolyPlayer = player  # type: ignore
        space = self._pending_purchase_space()
        if not space:
            return
        if space.space_id in self.property_owners:
            self.turn_pending_purchase_space_id = ""
            return
        if mono_player.cash < space.price:
            return

        mono_player.cash -= space.price
        mono_player.owned_space_ids.append(space.space_id)
        self.property_owners[space.space_id] = mono_player.id
        if space.space_id in self.mortgaged_space_ids:
            self.mortgaged_space_ids.remove(space.space_id)
        self.turn_pending_purchase_space_id = ""

        self.broadcast_l(
            "monopoly-property-bought",
            player=mono_player.name,
            property=space.name,
            price=space.price,
            cash=mono_player.cash,
        )

        if self.turn_can_roll_again:
            self._prepare_next_roll_after_doubles(mono_player)

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_auction_property(self, player: Player, action_id: str) -> None:
        """Resolve pending property via automatic auction."""
        mono_player: MonopolyPlayer = player  # type: ignore
        space = self._pending_purchase_space()
        if not space:
            return

        self.turn_pending_purchase_space_id = ""
        self._run_property_auction(space, mono_player)
        if self.turn_can_roll_again and not mono_player.bankrupt:
            self._prepare_next_roll_after_doubles(mono_player)

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_mortgage_property(
        self, player: Player, space_id: str, action_id: str
    ) -> None:
        """Mortgage one owned property to raise cash."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if space_id not in self._options_for_mortgage_property(player):
            return
        space = SPACE_BY_ID.get(space_id)
        if not space:
            return

        value = self._mortgage_value(space)
        mono_player.cash += value
        self.mortgaged_space_ids.append(space_id)
        self.broadcast_l(
            "monopoly-property-mortgaged",
            player=mono_player.name,
            property=space.name,
            amount=value,
            cash=mono_player.cash,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_unmortgage_property(
        self, player: Player, space_id: str, action_id: str
    ) -> None:
        """Unmortgage one owned property."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if space_id not in self._options_for_unmortgage_property(player):
            return
        space = SPACE_BY_ID.get(space_id)
        if not space:
            return

        cost = self._unmortgage_cost(space)
        if mono_player.cash < cost:
            return
        mono_player.cash -= cost
        self.mortgaged_space_ids.remove(space_id)
        self.broadcast_l(
            "monopoly-property-unmortgaged",
            player=mono_player.name,
            property=space.name,
            amount=cost,
            cash=mono_player.cash,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_build_house(self, player: Player, space_id: str, action_id: str) -> None:
        """Build one house/hotel on an owned eligible street property."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if space_id not in self._options_for_build_house(player):
            return
        space = SPACE_BY_ID.get(space_id)
        if not space or not self._is_street_property(space):
            return

        cost = max(0, space.house_cost)
        if mono_player.cash < cost:
            return

        if not self._can_raise_building_level(space_id):
            return
        mono_player.cash -= cost
        new_level = self._building_level(space_id) + 1
        self._set_building_level(space_id, new_level)
        self.broadcast_l(
            "monopoly-house-built",
            player=mono_player.name,
            property=space.name,
            amount=cost,
            level=new_level,
            cash=mono_player.cash,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_sell_house(self, player: Player, space_id: str, action_id: str) -> None:
        """Sell one house/hotel from an owned eligible street property."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if space_id not in self._options_for_sell_house(player):
            return
        space = SPACE_BY_ID.get(space_id)
        if not space or not self._is_street_property(space):
            return

        current_level = self._building_level(space_id)
        if current_level <= 0:
            return
        if not self._can_lower_building_level(space_id):
            return

        value = max(0, space.house_cost // 2)
        self._set_building_level(space_id, current_level - 1)
        new_level = self._building_level(space_id)
        mono_player.cash += value
        self.broadcast_l(
            "monopoly-house-sold",
            player=mono_player.name,
            property=space.name,
            amount=value,
            level=new_level,
            cash=mono_player.cash,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_offer_trade(self, player: Player, option: str, action_id: str) -> None:
        """Create a pending trade offer for another player."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if self.pending_trade_offer is not None:
            return
        if option not in self._options_for_offer_trade(player):
            return
        parsed = self._parse_trade_option(option)
        if not parsed:
            return

        target = self.get_player_by_id(parsed.target_id)
        if not target or not isinstance(target, MonopolyPlayer):
            return
        parsed.proposer_id = mono_player.id
        if not self._is_trade_offer_valid(mono_player, target, parsed):
            return

        self.pending_trade_offer = parsed
        self.broadcast_l(
            "monopoly-trade-offered",
            proposer=mono_player.name,
            target=target.name,
            offer=parsed.summary,
        )

        if target.is_bot:
            if self._bot_accepts_trade_offer(mono_player, target, parsed) and self._apply_trade_offer(
                mono_player, target, parsed
            ):
                self.broadcast_l(
                    "monopoly-trade-completed",
                    proposer=mono_player.name,
                    target=target.name,
                    offer=parsed.summary,
                )
            else:
                self.broadcast_l(
                    "monopoly-trade-declined",
                    proposer=mono_player.name,
                    target=target.name,
                    offer=parsed.summary,
                )
            self.pending_trade_offer = None

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_accept_trade(self, player: Player, action_id: str) -> None:
        """Accept the currently pending trade for this player."""
        mono_player: MonopolyPlayer = player  # type: ignore
        offer = self._pending_trade_for_target(mono_player)
        if offer is None:
            return
        proposer = self.get_player_by_id(offer.proposer_id)
        if not proposer or not isinstance(proposer, MonopolyPlayer):
            self.pending_trade_offer = None
            self.rebuild_all_menus()
            return

        if not self._apply_trade_offer(proposer, mono_player, offer):
            self.broadcast_l(
                "monopoly-trade-cancelled",
                offer=offer.summary,
            )
            self.pending_trade_offer = None
            self._sync_cash_scores()
            self.rebuild_all_menus()
            return

        self.broadcast_l(
            "monopoly-trade-completed",
            proposer=proposer.name,
            target=mono_player.name,
            offer=offer.summary,
        )
        self.pending_trade_offer = None
        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_decline_trade(self, player: Player, action_id: str) -> None:
        """Decline the currently pending trade for this player."""
        mono_player: MonopolyPlayer = player  # type: ignore
        offer = self._pending_trade_for_target(mono_player)
        if offer is None:
            return
        proposer = self.get_player_by_id(offer.proposer_id)
        proposer_name = proposer.name if proposer and isinstance(proposer, MonopolyPlayer) else "Unknown"
        self.broadcast_l(
            "monopoly-trade-declined",
            proposer=proposer_name,
            target=mono_player.name,
            offer=offer.summary,
        )
        self.pending_trade_offer = None
        self.rebuild_all_menus()

    def _action_pay_bail(self, player: Player, action_id: str) -> None:
        """Pay bail to leave jail before rolling."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if not mono_player.in_jail or self.turn_has_rolled or mono_player.cash < BAIL_AMOUNT:
            return

        mono_player.cash -= BAIL_AMOUNT
        mono_player.in_jail = False
        mono_player.jail_turns = 0
        self.broadcast_l(
            "monopoly-bail-paid",
            player=mono_player.name,
            amount=BAIL_AMOUNT,
            cash=mono_player.cash,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_use_jail_card(self, player: Player, action_id: str) -> None:
        """Use a get-out-of-jail-free card."""
        mono_player: MonopolyPlayer = player  # type: ignore
        if not mono_player.in_jail or self.turn_has_rolled or mono_player.get_out_of_jail_cards <= 0:
            return

        mono_player.get_out_of_jail_cards -= 1
        mono_player.in_jail = False
        mono_player.jail_turns = 0
        self.broadcast_l(
            "monopoly-jail-card-used",
            player=mono_player.name,
            cards=mono_player.get_out_of_jail_cards,
        )

        self._sync_cash_scores()
        self.rebuild_all_menus()

    def _action_end_turn(self, player: Player, action_id: str) -> None:
        """End current player's turn and advance."""
        self._reset_turn_state()
        next_player = self.advance_turn(announce=True)
        if next_player and next_player.is_bot:
            BotHelper.jolt_bot(next_player, ticks=random.randint(8, 14))

    def on_tick(self) -> None:
        """Run per-tick updates (bot actions)."""
        super().on_tick()
        BotHelper.on_tick(self)

    def bot_think(self, player: MonopolyPlayer) -> str | None:
        """Simple scaffold bot logic."""
        pending_offer = self._pending_trade_for_target(player)
        if pending_offer:
            proposer = self.get_player_by_id(pending_offer.proposer_id)
            if proposer and isinstance(proposer, MonopolyPlayer):
                if self._bot_accepts_trade_offer(proposer, player, pending_offer):
                    return "accept_trade"
            return "decline_trade"

        if player.in_jail and not self.turn_has_rolled:
            if player.get_out_of_jail_cards > 0:
                return "use_jail_card"
            if player.cash >= BAIL_AMOUNT and player.jail_turns >= 2:
                return "pay_bail"
        if not self.turn_has_rolled:
            return "roll_dice"
        pending_space = self._pending_purchase_space()
        if pending_space:
            if self._can_buy_pending_space(player) and player.cash - pending_space.price >= 200:
                return "buy_property"
            return "auction_property"
        if self.turn_can_roll_again:
            return "roll_dice"
        return "end_turn"

    def on_start(self) -> None:
        """Start scaffold mode using the selected preset metadata."""
        self.status = "playing"
        self.game_active = True
        self.round = 1

        active_players = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([player.name for player in active_players])
        self.set_turn_players(active_players)

        preset = self._resolve_selected_preset()
        self.active_preset_id = preset.preset_id
        self.active_preset_name = preset.name
        self.active_family_key = preset.family_key
        self.active_edition_ids = list(preset.edition_ids)
        self.active_anchor_edition_id = preset.anchor_edition_id
        self.property_owners.clear()
        self.mortgaged_space_ids.clear()
        self.building_levels = {
            space.space_id: 0 for space in CLASSIC_STANDARD_BOARD if self._is_street_property(space)
        }
        self.pending_trade_offer = None
        self._reset_turn_state()
        self.turn_doubles_count = 0

        self.chance_deck_order = CHANCE_CARD_IDS.copy()
        self.community_chest_deck_order = COMMUNITY_CHEST_CARD_IDS.copy()
        random.shuffle(self.chance_deck_order)
        random.shuffle(self.community_chest_deck_order)
        self.chance_deck_index = 0
        self.community_chest_deck_index = 0

        for player in active_players:
            if isinstance(player, MonopolyPlayer):
                player.position = 0
                player.cash = STARTING_CASH
                player.owned_space_ids.clear()
                player.bankrupt = False
                player.in_jail = False
                player.jail_turns = 0
                player.get_out_of_jail_cards = 0

        self._sync_cash_scores()

        self.broadcast_l(
            "monopoly-scaffold-started",
            preset=preset.name,
            count=len(self.active_edition_ids),
        )

        self.announce_turn(turn_sound="game_pig/turn.ogg")
        BotHelper.jolt_bots(self, ticks=random.randint(12, 20))
        self.rebuild_all_menus()
