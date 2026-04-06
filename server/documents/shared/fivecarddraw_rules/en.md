# Rules Of Five Card Draw
PlayPalace team, 2026.

## TL;DR
Five Card Draw is the classic form of poker. Each player is dealt five cards, there is a round of betting, then each player may discard and replace up to three cards (or four if holding an ace). A second round of betting follows, and the best five-card poker hand wins the pot. The game continues hand after hand until only one player has chips remaining.

## Gameplay
A game of Five Card Draw supports 2 to 5 players. Each player begins with a stack of chips. The game is played as a series of hands, and a dealer button rotates clockwise after every hand to determine betting order.

### Antes
At the start of each hand, every player posts an ante -- a forced bet that seeds the pot. If your chip stack is smaller than the ante, you are forced all-in for whatever you have left.

### The Deal
Each player is dealt five cards face-down, starting with the player to the left of the dealer button and going clockwise. Your cards are sorted automatically and announced to you after the deal.

### First Betting Round
After the deal, a round of betting begins with the player to the left of the dealer button. On your turn you may:

* **Call/Check:** Match the current bet (or check if no one has bet yet). If you have fewer chips than the bet, calling puts you all-in.
* **Raise:** Increase the bet. You must raise by at least the size of the previous raise. In no-limit mode there is no cap on raise size. In pot-limit or double-pot-limit mode, raises are capped relative to the pot size. If a maximum number of raises has been set, no further raises are allowed once that cap is reached.
* **All-in:** Commit all of your remaining chips.
* **Fold:** Surrender your hand and forfeit any chips you have already put into the pot.

If all but one player folds, that player wins the pot immediately and a new hand begins.

### The Draw Phase
After the first betting round, each player (starting from the left of the dealer button) may discard cards and receive replacements from the deck. You toggle individual cards for discard and then confirm your draw:

* You may discard up to 3 cards normally.
* If you hold an ace, you may discard up to 4 cards.
* You may also stand pat -- keep all five cards -- by confirming the draw without marking any cards for discard.

Discarded cards are replaced from the deck. Other players are told how many cards you drew (or that you stood pat), but never which cards.

### Second Betting Round
After all players have drawn, a second round of betting takes place using the same rules as the first.

### Showdown
If two or more players remain after the second betting round, a showdown occurs. All remaining hands are revealed and the best hand wins the pot. If there are side pots (because one or more players went all-in for different amounts), each pot is awarded separately.

### Winning the Game
The game continues hand after hand. Players who lose all their chips are eliminated. The last player with chips wins the game.

## Poker Hand Rankings
Hands are ranked from highest to lowest as follows. In each case, if two players have the same category of hand, the one with the higher card values wins. If they are exactly tied, the pot is split.

1. **Royal Flush:** A, K, Q, J, 10 all of the same suit. The highest possible hand.
2. **Straight Flush:** Five consecutive cards of the same suit (for example, 6-7-8-9-10 of hearts).
3. **Four of a Kind:** Four cards of the same rank (for example, four kings). The higher rank wins ties.
4. **Full House:** Three of a kind plus a pair (for example, three jacks and two sevens). The three-of-a-kind rank is compared first.
5. **Flush:** Five cards of the same suit, not in sequence. The highest card in the flush determines the winner; if tied, compare the next highest, and so on.
6. **Straight:** Five consecutive cards of mixed suits (for example, 4-5-6-7-8). Ace can be high (A-K-Q-J-10) or low (A-2-3-4-5). The highest top card wins.
7. **Three of a Kind:** Three cards of the same rank. The higher rank wins ties.
8. **Two Pair:** Two separate pairs (for example, two aces and two fives). The higher pair is compared first, then the lower pair, then the remaining card (the kicker).
9. **One Pair:** A single pair. The pair rank is compared first; if tied, kickers are compared in order.
10. **High Card:** No matching ranks or sequences. The highest card wins; if tied, compare the next highest, and so on.

### Customizable Options
The host can adjust several settings before the game starts:

* **Starting Chips:** The number of chips each player begins with. Defaults to 20,000 and can be set from 100 to 1,000,000.
* **Ante:** The forced bet each player posts at the start of every hand. Defaults to 100 and can be set from 0 to 1,000,000. Setting it to 0 disables antes entirely.
* **Turn Timer:** A time limit for each player's turn. Options are 5, 10, 15, 20, 30, 45, 60, or 90 seconds, or unlimited (the default). If a player's timer expires, they fold during a betting round or automatically confirm their draw during the draw phase.
* **Raise Mode:** Controls how raises are capped. Options are no-limit (default, no cap on raise size), pot-limit (raises capped at the current pot size), and double-pot-limit (raises capped at twice the current pot size).
* **Max Raises:** The maximum number of raises allowed in a single betting round. Defaults to 0, which means unlimited. Can be set from 0 to 10.

### Example Hand
Three players are at the table: Alice, Bob, and Carol. The ante is 100 and everyone starts with 20,000 chips. Alice is the dealer this hand.

The ante is posted: 100 from each player. The pot is 300.

Cards are dealt. Bob (left of the dealer) acts first. He has a pair of kings and checks. Carol also checks. Alice, holding nothing useful, checks too. No one has bet, so the betting round ends.

Draw phase. Bob keeps his pair of kings and one high kicker, discarding the other two cards. He draws two replacements. Carol has four hearts and is chasing a flush; she discards the one non-heart and draws one card. Alice has nothing and discards three cards, drawing three new ones.

Second betting round. Bob picked up a third king and now has three of a kind. He raises 200. Carol missed her flush and folds. Alice picked up a pair of nines but does not want to call into Bob's raise. She folds too. Bob wins the pot of 500 uncontested.

## Keyboard Shortcuts
All shortcuts specific to Five Card Draw:

### Betting Actions
* F: Fold.
* C: Call or check (matches the current bet, or checks if there is no bet to match).
* R: Raise (you will be prompted to enter a raise amount).
* Shift+A: Go all-in.

### Draw Phase
* 1 through 5: Toggle discard on card 1 through card 5. Pressing a number key marks that card for discard; pressing it again unmarks it. The game announces whether the card is now held or marked for discard.
* D: Confirm your draw. Discards all marked cards and draws replacements. If no cards are marked, you stand pat.

### Information
* W: Read your entire hand aloud.
* G: Announce your current hand value (for example, "pair of aces" or "king-high flush").
* 1 through 5 (outside draw phase): Read a specific card by position.
* P: Check the current pot size.
* N: Check the current bet you need to call.
* M: Check the minimum raise amount.
* H: Check which players are still in the hand.
* X: Check who the dealer is.
* Z: Check your seating position relative to the dealer.
* Shift+T: Check the turn timer.
* S: Check chip counts (scores).
* Shift+S: View detailed chip counts.
* T: Check whose turn it is.

## Game Theory / Tips
* **Starting hands matter.** In Five Card Draw there are no community cards, so you must judge your hand entirely on what you hold. Pairs or better are worth playing; hands with no pair and no draw potential are usually worth folding if there is any significant bet.
* **Position is powerful.** The later you act in a betting round, the more information you have about what other players did. The dealer acts last and has the biggest advantage.
* **Pay attention to how many cards opponents draw.** A player who draws one card is likely chasing a straight or flush, or already has two pair. A player who draws three is starting from a pair. A player who stands pat either has a very strong hand or is bluffing.
* **Do not chase flushes and straights too aggressively.** Drawing one card to a four-card flush gives you roughly a 1-in-5 chance of completing it. That is often not enough to justify calling a large bet.
* **Three of a kind is a very strong hand in Five Card Draw.** It wins most showdowns. If you have trips, consider raising to build the pot rather than slow-playing.
* **Bluffing works best against fewer opponents.** With five players at the table, someone is likely to have a real hand. With two players, a well-timed bluff standing pat can convince your opponent to fold.
* **Mind your chip stack.** If you are short-stacked, look for a decent hand and commit. If you have a big stack, use it to pressure shorter stacks with raises.
