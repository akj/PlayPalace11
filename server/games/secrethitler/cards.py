"""Policy / Role / Party / Power enums and deck composition for Secret Hitler."""

from enum import Enum


class Policy(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"


class Party(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"


class Role(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"
    HITLER = "hitler"

    @property
    def party(self) -> Party:
        if self is Role.LIBERAL:
            return Party.LIBERAL
        return Party.FASCIST


class Power(str, Enum):
    NONE = "none"
    INVESTIGATE = "investigate"
    SPECIAL_ELECTION = "special_election"
    POLICY_PEEK = "policy_peek"
    EXECUTION = "execution"


ROLE_COUNTS: dict[int, tuple[int, int, int]] = {
    5: (3, 1, 1),
    6: (4, 1, 1),
    7: (4, 2, 1),
    8: (5, 2, 1),
    9: (5, 3, 1),
    10: (6, 3, 1),
}


FASCIST_TRACK_POWERS: dict[str, tuple[Power, Power, Power, Power, Power]] = {
    "5-6": (Power.NONE, Power.NONE, Power.POLICY_PEEK, Power.EXECUTION, Power.EXECUTION),
    "7-8": (Power.NONE, Power.INVESTIGATE, Power.SPECIAL_ELECTION, Power.EXECUTION, Power.EXECUTION),
    "9-10": (
        Power.INVESTIGATE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    ),
}


def track_bucket_for(player_count: int) -> str:
    """Return the fascist-track bucket key for a given player count."""
    if 5 <= player_count <= 6:
        return "5-6"
    if 7 <= player_count <= 8:
        return "7-8"
    if 9 <= player_count <= 10:
        return "9-10"
    raise ValueError(f"Unsupported player count: {player_count}")


def build_policy_deck() -> list[Policy]:
    """Return a fresh, unshuffled 17-card deck: 6 liberal + 11 fascist."""
    return [Policy.LIBERAL] * 6 + [Policy.FASCIST] * 11
