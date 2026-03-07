# Pig game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-pig = Svinja
pig-category = Igre sa kockicama

# Actions
pig-roll = Baci kockicu
pig-bank = Sačuvaj { $points } poena

# Game events (Pig-specific)
pig-rolls = { $player } baca kockicu...
pig-roll-result = { $roll }, ukupno { $total }
pig-bust = O ne, jedinica! { $player } gubi { $points } poena.
pig-bank-action = { $player } odlučuje da sačuva { $points }, što je ukupno { $total }
pig-winner = Imamo pobednika, i to je { $player }!

# Pig-specific options
pig-set-min-bank = Najmanji rezultat dozvoljen za čuvanje: { $points }
pig-set-dice-sides = Stranice kockice: { $sides }
pig-enter-min-bank = Upišite najmanji broj poena dozvoljen za čuvanje:
pig-enter-dice-sides = Upišite broj stranica kockice:
pig-option-changed-min-bank = Najmanji broj poena za čuvanje podešen na { $points }
pig-option-changed-dice = Kockica sada ima { $sides } stranica

# Disabled reasons
pig-need-more-points = Potrebno vam je još poena za čuvanje.

# Validation errors
pig-error-min-bank-too-high = Najmanji broj poena za čuvanje mora biti manji od konačnog rezultata.
