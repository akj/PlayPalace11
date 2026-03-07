# Pig game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-pig = Pig
pig-category = Dice Games

# Actions
pig-roll = Roll the die
pig-bank = Bank { $points } points

# Game events (Pig-specific)
pig-rolls = { $player } rolls the die...
pig-roll-result = A { $roll }, for a total of { $total }
pig-bust = Oh no, a 1! { $player } loses { $points } points.
pig-bank-action = { $player } decides to bank { $points }, for a total of { $total }
pig-winner = We have a winner, and it is { $player }!

# Pig-specific options
pig-desc-target-score = The score needed to win the game

pig-set-min-bank = Minimum bank: { $points }
pig-desc-min-bank = Minimum round score required before banking is allowed
pig-enter-min-bank = Enter the minimum points to bank:
pig-option-changed-min-bank = Minimum bank points changed to { $points }

pig-set-dice-sides = Dice sides: { $sides }
pig-desc-dice-sides = What type of dice to use
pig-enter-dice-sides = Enter the number of dice sides:
pig-option-changed-dice = Dice now has { $sides } sides

# Disabled reasons
pig-need-more-points = You need more points to bank.

# Validation errors
pig-error-min-bank-too-high = Minimum bank points must be less than the target score.
