# Monopoly City Anchor Notes (monopoly-1790)

## Source
- Edition ID: `monopoly-1790`
- Policy: `anchor-first`
- Curated catalog file: `server/games/monopoly/catalog/monopoly_manual_variants_curated.json`
- Catalog locales found for this edition: `en-ca`, `en-hk`, `en-my`, `en-nz`, `en-sg`, `en-us`
- Manual URL (`en-us` PDF): `https://assets-us-01.kc-usercontent.com:443/500e0a65-283d-00ef-33b2-7f1f20488fe2/406d286e-41f1-44bd-9083-47d0d4f87a72/799fd741eae7a6640b7dbb78d6e9635d.pdf`
- Instruction page (`en-us`): `https://instructions.hasbro.com/en-us/instruction/monopoly-city`
- Text extraction artifact used for rule normalization: `/tmp/monopoly-city-rjina.txt`

## Extraction Notes
- OCR/text extraction shows currency as `a` (for example, `a500 k`, `a2m`, `a7m`).
- Normalized values in this document use integer amounts in base units:
  - `10k` -> `10000`
  - `500k` -> `500000`
  - `1m` -> `1000000`
  - `2m` -> `2000000`
  - `7m` -> `7000000`

## Rules Extract

### Setup
- Separate the Rent Dodge card from Chance and place it next to Free Parking (lines 227-229).
- Shuffle Chance cards face down next to the board (line 231).
- All players choose movers and place them on GO (line 233).
- Banker controls money, District cards, buildings, and auctions (lines 237-243).

### Turn flow
- On each turn: roll and move, resolve landing space, then optionally build (lines 283-289).
- Rolling a double grants another roll and another resolve/build cycle (lines 287-289).
- Build can be used on every turn/roll, but only one build-button press per roll (lines 339, 391-393).
- Unowned district: buy or mandatory auction if declined (lines 299-306).
- Owned district (other player): pay rent (lines 307-310).
- Own district with railroad: may jump to another railroad district and resolve destination ownership (line 313).

### Space/action effects
- Auction space: choose any unowned district to auction (lines 315-317).
- Industry Tax: pay printed amount only if player owns any industrial buildings (lines 319-321).
- Planning Permission: build one hazard or one bonus building (lines 323-325, 397-410).
- Free Parking: take Rent Dodge card (lines 327-329, 517-523).
- Chance space: draw and follow Chance card (line 333).
- Go To Jail: move to jail and do not collect for passing GO (lines 335-337, 543-547).

### Payment/economy rules
- Build up to 8 blocks per district (line 339).
- Hazards make residential blocks worthless; industrial blocks still count for rent (lines 343, 351, 465-500).
- Railroad build can be free when build icon indicates railroad (`D`) (lines 357, 385).
- Railroad jump from an owned-by-other district requires paying rent before leaving (line 363).
- Auction timing: up to 50 seconds; bidding may start from 10k (lines 371-374).
- Bonus and hazard buildings are free, do not count toward 8-block cap, and mutually exclude each other (lines 411-415).
- Stadium: cost 2m; +1m income on each pass GO; max one per color group (lines 435, 441-446).
- Skyscraper doubles rent for one color group when full group owned (lines 425-432).
- Monopoly Tower: cost 7m; doubles rent value of every district owned (lines 417-423).
- Skyscraper and Tower doubling do not stack (lines 501-503).
- Hazard removal cost: 500k per block in hazard (lines 467-473).
- Mortgage value equals district current rent value; buyback repays same value (lines 527-531).
- Bankruptcy:
  - Owing bank: district cards return to banker, then auctioned (lines 533-535).
  - Owing another player: creditor gets remaining money, district cards, and get-out-of-jail cards (lines 537-539).
- Jail release: pay 500k fine, use card, or roll doubles; after 3 failed turns must pay 500k and move by roll (lines 549-555).

### Win condition
- Final value at game end is:
  - cash on hand
  - plus current rent value of all owned districts
  - richest player wins (lines 29-39, 295).

### Tie-break rules
- No explicit tie-break procedure found in extracted anchor text.
- Deterministic implementation rule for first pass: if tied on final value, choose earliest turn-order contender (documented engine fallback).

## Normalized Rule Table
| Rule Key | Anchor Text | Normalized Value | Confidence |
|---|---|---|---|
| `city.win.final_value_formula` | "Count your cash... work out the rent value... add them together" (29-37) | `cash + sum(current_rent_value_per_owned_district)` | high |
| `city.win.selector` | "The richest player wins" (39, 295) | `max(final_value)` | high |
| `city.win.tiebreak` | Not specified in extracted text | `turn_order_first` fallback | medium |
| `city.setup.start_space` | "put [movers] on the GO space" (233) | `start_on_go=true` | high |
| `city.setup.rent_dodge_location` | "Separate the Rent Dodge card... next to Free Parking" (227) | `rent_dodge_starts_at_free_parking=true` | high |
| `city.turn.double_extra_turn` | "If you rolled a double, take another turn" (287-289) | `doubles_grant_extra_turn=true` | high |
| `city.turn.build_button_presses_per_roll` | "You can press the Build button once per turn" (391-393) | `1` | high |
| `city.board.unowned_district_decline` | "If you don't want to buy it, you MUST auction it" (305) | `auction_required=true` | high |
| `city.board.industrial_tax_gate` | "Pay... if you own any industrial buildings. If you don't, do nothing." (319-321) | `tax_applies_if_industrial_count>0` | high |
| `city.build.max_blocks_per_district` | "BUILD UP TO 8 BLOCKS ON EACH DISTRICT" (339) | `8` | high |
| `city.build.railroad.cost` | "build a railroad on any district for free" (357) | `0` | high |
| `city.build.railroad.owned_jump_requires_rent` | "must pay the rent before you leave" (363) | `true` | high |
| `city.auction.timer_seconds` | "Each auction lasts up to 50 seconds" (371) | `50` | high |
| `city.auction.min_opening_bid` | "starts the bidding... from a10k" (373-374) | `10000` | high |
| `city.planning_permission.choice` | "build a bonus... OR build a hazard" (401-409) | `exactly_one_of_bonus_or_hazard` | high |
| `city.planning_permission.cost` | "Hazards and bonus buildings are free" (415) | `0` | high |
| `city.planning_permission.mutual_exclusion` | "BONUS... PREVENT HAZARDS..., and HAZARDS PREVENT BONUS..." (411) | `true` | high |
| `city.stadium.cost` | "Stadiums COST: a2m" (435) | `2000000` | high |
| `city.stadium.pass_go_bonus` | "Collect a1m per stadium... every time you pass GO" (443) | `1000000` | high |
| `city.tower.cost` | "Monopoly Tower COST: a7m" (417) | `7000000` | high |
| `city.rent.hazard_residential_counts` | "residential... become worthless" (465) | `false` | high |
| `city.rent.hazard_industrial_counts` | "Hazard? Count the industrial blocks only" (499) | `true` | high |
| `city.rent.double_sources` | "skyscraper... OR the MONOPOLY Tower... Double the rent" (501-503) | `skyscraper_or_tower` | high |
| `city.rent.double_stack` | "cannot double the rent twice" (503) | `false` | high |
| `city.hazard.remove_cost_per_block` | "paying a500k per block" (467) | `500000` | high |
| `city.jail.fine` | "Paying... a500k fine" (551) | `500000` | high |
| `city.jail.max_double_attempts` | "If you haven't rolled a double after three turns" (555) | `3` | high |
| `city.mortgage.value_basis` | "mortgage value is... current rent value" (527) | `current_rent_value` | high |
| `city.mortgage.buyback_value` | "pay the rent value... amount you received" (531) | `same_as_mortgage_value` | high |
| `city.free_parking.rent_dodge_behavior` | "collect the Rent Dodge card... use later... give to next player if not used" (517-523) | `single_shared_token` | high |
| `city.bankruptcy.owing_bank` | "Return... to banker who will auction" (533-535) | `assets_to_bank_then_auction` | high |
| `city.bankruptcy.owing_player` | "other player receives... money... District cards" (537-539) | `assets_to_creditor` | high |
