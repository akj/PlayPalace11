# 21 (Survival Rules)

## Status

Implemented in `server/games/twentyone/game.py`.

## Attribution

Contributed by Drew Mochak (objectinspace) with OpenAI Codex.
Inspired by the game mode of the same name from Capcom's Resident Evil 7 banned footage DLC.

## Overview

This game resembles blackjack: the deck has eleven cards numbered 1-11, and the total of your hand must be closer to (usually) 21 than your opponent to win.

## Round Flow

- Both players receive 2 number cards. The first is hidden so only you can see it, whereas the second card is visible to everyone.
- you can `hit` to draw another card, `stand` to end your turn, or play a change card if you have one.
- When you hit, other players will see what card was drawn. Both players pull from the same deck and there are no repeated numbers. 
- Hitting also creates a chance to draw a change card. These are hidden from your opponent.
- The round ends when all players stand without drawing or using a card.
- At the end of the round, your hidden number cards are revealed and your totals are compared with the target number, which is 21 by default. If you have exactly this number, or more than your opponent without going over, you win. If you have more than this number (bust) but your opponent has less, you lose. If you both bust, whoever is closer to the target wins. If you have the same total, everyone loses.

## Bets, Damage and scoring
You start with 0 points. Each round starts with a bet of 1 for each player. Some change cards alter this amount. At the end of the round, the loser will gain the number of points equal to their bet. Any player who Reaches 10 points loses the game.

## Change Card Summary

Change cards allow you to change the conditions of the game to be more favorable for your current hand. You can raise your opponent's bet, or lower your own. You can draw specific numbers from the deck if available, or draw the best card for your current situation. You can change the target from 21 to a different number, return you or your opponent's last drawn card to the top of the deck, or even negate your opponent's other change cards. The following is a list of each change card in the game, and a description. You can press c or select "change card guide" to reference this list. They are also read in the menu for selecting a change card.

- `raise one`: Opponent damage +1; gain 1 change card.
- `raise two`: Opponent damage +2; gain 1 change card.
- `withdraw and raise two`: Opponent damage +2; return opponent last card to top of deck; gain 1 change card.
- `defend`: Reduce incoming damage by 1.
- `defend enhanced`: Reduce incoming damage by 2.
- `best draw and raise five`: Best draw and increase opponent damage by 5.
- `best draw with change`: Best draw and gain 2 change cards.
- `draw 2`, `draw 3`, `draw 4`, `draw 5`, `draw 6`, `draw 7`: draw that number if available.
- `withdraw`: Return opponent last card to top of deck.
- `undraw`: Return your own last card to top of deck.
- `swap top cards`: Exchange your top card with the opponent's top card.
- `delete`: remove opponent's newest change card effect.
- `delete enhanced`: remove all opponent change card effects.
- `delete double enhanced`: Clear all opponent change card effects and prevent opponent from playing change cards for the rest of the round.
- `change-up`: Discard 2 change cards; gain 3 change cards.
- `change-up enhanced`: Discard 1 change card; gain 4 change cards.
- `embrace change`: Whenever any change card is played, gain 1 change card.
- `target 17`: Set round target to 17.
- `target 24`: Set round target to 24.
- `target 27`: Set round target to 27.
- `trojan horse`: Opponent draws the best available card for the current target.

Additional enemy-inspired change cards:

- `defensive offense`: Requires at least 3 of your defend effects already active. Removes up to 3; opponent damage +3 while active.
- `defensive offense enhanced`: Requires at least 2 of your defend effects already active. Removes up to 2; opponent damage +5 while active.
- `change is good`: Both players gain 1 change card.
- `cost of change`: Opponent damage increases by half their change-card count while active.
- `cost of change enhanced`: Opponent damage increases by their change-card count while active.
- `change for change's sake`: At round end, opponent discards half their change cards; breaks if they play 2 change cards in one turn.
- `change for change's sake enhanced`: At round end, opponent discards all change cards; breaks if they play 3 change cards in one turn.
- `risky change`: Gain 3 change cards; your own damage taken is +1 while active.
- `glitched draw`: Requires at least 1 other change card. Discard 1 random change card; opponent draws the highest available number card.
- `dark bargain`: Requires at least 2 other change cards. Discard half your change cards, draw your best card, and raise opponent damage by 10 while active.
- `run away!`: If you would lose a round, consume this effect and take no damage.
- `21 at 21`: While your hand total is exactly 21, opponent damage increases by 21.
- `nope`: Cancel the current round and immediately begin a new one.
- `no draw for you!`: Opponent cannot draw number cards from hits or change-card effects while active.
- `game over`: Both players' damage is increased by 100, and opponent cannot draw cards while active.

## Keybinds

- `1`: Hit
- `2`: Stand
- `3`: Play change card
- `4`: Check 21 status
- `C`: Change card guide
- `O`: Read opponent face-up cards
- `R`: Read current hand
- `B`: Read current bets
- `E`: Read active change-card effects

## Tips And Strategy

- The limited number of cards makes it easier to guess your opponent's bottom card in advance. These possibilities narrow further the more cards that are drawn.
- The change cards to draw specific numbers can also be used to guess an opponent's bottom card. The number will only be drawn if it is available in the deck to be drawn. Therefore, if it is not drawn, not in your hand, and not visible in the opponent's hand, it is your opponent's bottom card.
- Without knowing your opponent's bottom card, the safest strategy is to determine the best number they could have, then play as if they have it. Don't be afraid to change this guess as the round progresses.
- To win the game, your opponent needs to score 10 before you do. If you can't win outright, use change cards so the loss costs you less points.

## Test Coverage

Covered by `server/tests/test_twentyone.py`, including:

- Hidden/public card visibility rules
- Turn and stand-resolution behavior
- Change card visibility and playability
- Keybind mappings and readout actions
- Top-of-deck return behavior for removed face-up cards
- Target-card playability guard for already-active target value
- Target-proximity cue only on exact target total for the acting player
- Bot play with save/reload round-trip
