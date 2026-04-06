# Rules Of Twenty One
PlayPalace team, 2026.

## TL;DR
Twenty One (Survival Rules) is a two-player card game where you try to get as close to a target number (usually 21) as possible without going over. Unlike standard blackjack, this is a survival game: each player has a pool of hit points, and you play round after round until someone runs out of HP. A layer of tactical modifier cards adds bluffing, disruption, and resource management on top of the core draw-or-stand decision.

## Gameplay
The game is played in rounds. Each round, both players are dealt two cards from a deck of cards numbered 1 through 11. Your first card is hidden (a hole card that only you can see), and your second card is face-up (visible to your opponent). Players take turns choosing to hit (draw another face-up card), stand (lock in their total), or play a modifier card from their hand.

A round ends when both players have chosen to stand. At that point, totals are compared against the current target (21 by default). The player closer to the target without going over wins. If one player busts (exceeds the target) and the other does not, the non-busted player wins. If both bust, the player closer to the target wins. If totals are tied, the round is a draw and both players take damage.

The loser of a round takes damage equal to the current bet value. The bet starts at the base bet (default 1) and can be raised or lowered by modifier effects. When a player's HP reaches zero, they are eliminated and the other player wins the game.

Important: if either player hits or plays a modifier after one player has already chosen to stand, the standing player's stand is cancelled and they must act again. This prevents a player from locking in early and being helpless while the opponent manipulates the board.

At the start of each round, both players receive a number of random modifier cards (default 1). Additionally, each time you hit and draw a card, there is a chance (default 35 percent) of receiving another random modifier.

### Card Types
The deck contains cards ranked 1 through 11, with one copy of each per deck (configurable to use multiple decks). There are no suits. A fresh deck is shuffled at the start of every round.

### Modifier Cards
Modifier cards are the tactical heart of the game. You receive them at the start of each round and randomly when drawing cards. On your turn, instead of hitting or standing, you can play one modifier from your hand.

Some modifiers are instant effects that resolve immediately and are discarded. Others are table effects that persist for the rest of the round. Each player can have up to 5 table effects active at once; if you exceed the limit, your oldest effect is removed.

Here is the full list of modifier cards:

**Stake Modifiers (table effects):**
* Stake Raise 1: Increases opponent damage by 1 for the round. You also gain 1 random modifier.
* Stake Raise 2: Increases opponent damage by 2 for the round. You also gain 1 random modifier.
* Stake Raise 2+: Increases opponent damage by 2, returns opponent's last drawn face-up card to the top of the deck, and you gain 1 random modifier.

**Exact Draw Modifiers (instant):**
* Exact 2 through Exact 7: Searches the deck for a card of that exact rank and adds it to your hand. If no card of that rank remains, the modifier is wasted.

**Card Manipulation (instant):**
* Scrap Card: Removes your opponent's last drawn face-up card and places it on top of the deck.
* Recycle Card: Returns your opponent's last drawn face-up card to the top of the deck. (Functionally identical to Scrap in the current implementation.)
* Swap Draw: Both players return their last drawn face-up card to the deck, then each draws a new card.

**Modifier Management (instant):**
* Redraft: Discards 2 of your random modifiers, then gives you 3 new random modifiers. Net gain of 1.
* Redraft+: Discards 1 of your random modifiers, then gives you 4 new random modifiers. Net gain of 3.

**Defensive (table effects):**
* Guard: Reduces incoming round damage by 1 while active.
* Guard+: Reduces incoming round damage by 2 while active.

**Disruption (instant and table effects):**
* Break Effect: Destroys your opponent's newest table effect.
* Break All: Destroys all of your opponent's table effects.
* Lockdown (table effect): Clears all opponent table effects and prevents your opponent from playing any modifiers while Lockdown is active on your side.

**Precision Drawing:**
* Precision Draw (instant): Searches the deck and draws the best possible card for reaching the current target without going over. If already at or above the target, draws the card that gets closest.
* Precision Draw+ (table effect): Same as Precision Draw but also places a table effect that increases opponent damage by 5 for the round. Very powerful.
* Prime Draw (instant): Performs a precision draw and also gives you 2 random modifiers.

**Target Modifiers (table effects):**
* Target 17: Changes the round target to 17 for both players.
* Target 24: Changes the round target to 24 for both players.
* Target 27: Changes the round target to 27 for both players.
* Note: playing a target modifier removes all existing target modifiers from both players. Only one target modifier can be in effect at a time.

**Other:**
* Salvage (table effect): Whenever any player plays a modifier, you gain 1 random modifier. This triggers for every modifier played while Salvage is active.
* Aid Rival (instant): Your opponent draws their best possible card for the current target. This is a negative modifier that helps your opponent. You may receive it randomly and be stuck with it in your hand.

### Customizable Options
The host can adjust these settings before starting:

* **Starting Health:** How much HP each player begins with. Default is 10.
* **Base Bet:** The base damage dealt to the loser of each round, before modifier adjustments. Default is 1.
* **Starting Modifiers Per Round:** How many random modifier cards each player receives at the start of each round. Default is 1.
* **Draw Modifier Chance:** The percentage chance of gaining a random modifier each time you hit. Default is 35 percent.
* **Deck Count:** How many copies of the 1-through-11 deck to shuffle together. Default is 1 (11 cards total). More decks mean more cards available and less predictability.

### Example Round
Both players start with 10 HP. The base bet is 1 and the target is 21.

You are dealt a hidden 7 and a face-up 9. Your total is 16. Your opponent shows a face-up 5; their hole card is hidden.

You also receive a random modifier: Guard.

It is your turn. You are at 16, which is decent but risky. You decide to hit. You draw a 3, bringing your total to 19. Nice. You also get lucky and receive a random modifier from the draw: Stake Raise 1.

You play Stake Raise 1 as a table effect. Your opponent will now take 2 damage instead of 1 if they lose. Playing the modifier also gives you another random modifier.

Your opponent hits and draws a 6. Their shown total (from face-up cards) is 11, but their hidden card is unknown to you. They choose to stand.

You are happy with 19, so you stand as well. Both players have stood, so the round resolves.

Your opponent reveals their hole card: it was a 4. Their total is 15. Your total is 19. You are closer to 21 without busting, so you win the round.

Your opponent takes 2 damage (base bet 1, plus 1 from your Stake Raise 1). They drop to 8 HP. You remain at 10 HP.

A new round begins.

## Keyboard Shortcuts
Shortcuts specific to Twenty One:

* 1: Hit (draw a card).
* 2: Stand (lock in your total).
* 3: Play Modifier (opens a menu to select which modifier to play from your hand).
* 4: Check 21 status (announces your target, HP, bet, hand, modifiers, table effects, and visible opponent info).
* M: Modifier Guide (reads out every modifier and its description).
* O: Read opponent face-up cards (announces what your opponent is showing and their visible total).
* R: Read current hand (announces your cards and total).
* B: Read current bets (announces the effective bet for each player after modifier adjustments).
* E: Read active effects (announces the table effects for both players).
* S: Check scores (shows HP for all players).
* Shift+S: Detailed scores.

## Game Theory / Tips
* Your hole card is your biggest advantage. Only you know your true total. If your face-up cards look weak, your opponent may play aggressively and overextend. Use this information asymmetry.
* Standing is not permanent. If your opponent acts after you stand (hits or plays a modifier), your stand is cancelled. This means you cannot safely lock in early and ignore what your opponent does. Stay alert.
* Stake Raise modifiers are double-edged. They increase the punishment for your opponent if they lose, but they also take up one of your 5 table effect slots. If you stack too many offensive effects, you leave no room for Guard or other defensive options.
* Guard and Guard+ are most valuable when you are behind on HP. Reducing incoming damage from 3 to 1 can buy you multiple extra rounds to recover.
* Lockdown is extremely powerful if your opponent is holding modifiers. It clears their table effects and prevents them from playing anything. Time it well.
* Precision Draw and Prime Draw are best used when you are several points below the target. They guarantee the best available card, which takes randomness out of the equation.
* Target modifiers can swing a round dramatically. If you are sitting at 23 and would normally bust, playing Target 24 or Target 27 suddenly makes your hand legal. Conversely, if your opponent is at 20, dropping the target to 17 makes them bust instantly.
* Salvage is a slow-burn table effect. It rewards you every time any modifier is played, so it is strongest in modifier-heavy rounds. If both players are actively using modifiers, Salvage generates significant card advantage.
* Aid Rival is a trap modifier. If you are stuck with it, consider using Redraft or Redraft+ to cycle it out of your hand. Playing it gives your opponent an optimal draw, which is almost never what you want.
* Pay attention to your opponent's face-up cards and table effects. Use the O and E shortcuts frequently. Knowing their visible total helps you decide whether to push for a higher score or play defensively.
* With the default settings (10 HP, base bet 1), games tend to last many rounds. Small advantages compound over time. Do not take unnecessary risks when you have a lead.
