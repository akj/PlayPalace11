# 1-4-24 (Midnight) game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-midnight = 1-4-24
midnight-category = Igre sa kockicama

# Actions
midnight-roll = Baci kockice
midnight-keep-die = Zadrži { $value }
midnight-bank = Sačuvaj

# Game events
midnight-turn-start = { $player } je na potezu.
midnight-you-rolled = Dobili ste: { $dice }.
midnight-player-rolled = { $player } dobija: { $dice }.

# Keeping dice
midnight-you-keep = Zadržavate { $die }.
midnight-player-keeps = { $player } zadržava { $die }.
midnight-you-unkeep = ne zadržavate { $die }.
midnight-player-unkeeps = { $player } ne zadržava { $die }.

# Turn status
midnight-you-have-kept = Zadržane kockice: { $kept }. Preostalo bacanja: { $remaining }.
midnight-player-has-kept = { $player } zadržava: { $kept }. { $remaining } kockica preostalo.

# Scoring
midnight-you-scored = Dobili ste { $score } poena.
midnight-scored = { $player } dobija { $score } poena.
midnight-you-disqualified = Nemate i 1 i 4. Diskvalifikacija!
midnight-player-disqualified = { $player } nema i 1 i 4. Diskvalifikacija!

# Round results
midnight-round-winner = { $player } dobija rundu!
midnight-round-tie = Izjednačena runda između igrača { $players }.
midnight-all-disqualified = Svi igrači su diskvalifikovani! Nema pobednika ove runde.

# Game winner
midnight-game-winner = { $player } pobeđuje sa { $wins } dobijenih rundi!
midnight-game-tie = Izjednačeno! { $players } su dobili po { $wins } rundi.

# Options
midnight-set-rounds = Broj rundi za igranje: { $rounds }
midnight-enter-rounds = Upišite broj rundi za igranje:
midnight-option-changed-rounds = Broj rundi za igranje podešen na { $rounds }

# Disabled reasons
midnight-need-to-roll = Prvo morate da bacite kockice.
midnight-no-dice-to-keep = Nema dostupnih kockica za zadržavanje.
midnight-must-keep-one = Morate da zadržite bar jednu kockicu nakon bacanja.
midnight-must-roll-first = Prvo morate da bacite kockice.
midnight-keep-all-first = Morate da zadržite sve kockice pre čuvanja.
