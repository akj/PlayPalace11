# Rules Of Texas Hold'em
PlayPalace team, 2026.

## TL;DR
Texas Hold'em is the most widely played poker variant in the world. Each player is dealt two private hole cards, and five community cards are dealt face-up on the table across three stages (the flop, the turn, and the river). You make the best five-card hand you can from any combination of your two hole cards and the five community cards. Betting happens before the flop and after each community card stage. The last player standing after everyone else folds, or the player with the best hand at showdown, wins the pot. The game continues hand after hand until one player has all the chips.

## Gameplay
A game of Texas Hold'em supports 2 to 12 players. Every player starts with the same number of chips, and the game plays out over a series of hands.

### The Button and Blinds
Before each hand, a virtual dealer button rotates clockwise around the table. The button determines who posts the forced bets known as blinds:

* The player immediately after the button posts the **small blind**, which is half the big blind.
* The next player posts the **big blind**, which is the minimum bet for the hand.

In a heads-up (two-player) game, the button posts the small blind and the other player posts the big blind.

If antes are enabled, every player at the table puts in the ante amount before the hand begins, in addition to any blinds.

### Dealing
Each player is dealt two private cards face-down, known as hole cards. Only you can see your own hole cards. Cards are dealt starting from the player after the button, going clockwise, one card at a time for two rounds.

### Betting Rounds
There are up to four betting rounds per hand. On your turn, you can take one of the following actions:

* **Check:** Pass the action to the next player without putting in any chips. You can only check if no one has bet before you in the current round.
* **Call:** Match the current bet to stay in the hand.
* **Raise:** Increase the current bet. You must raise by at least the size of the last raise (or the big blind if no raise has occurred). Other players must then call, re-raise, or fold.
* **All In:** Put all your remaining chips into the pot. If your stack is smaller than the current bet, you can still go all in, but you can only win a proportional share of the pot.
* **Fold:** Surrender your cards and give up any claim to the pot.

If everyone folds except one player, that player wins the pot immediately without having to show their cards.

### The Four Stages
1. **Pre-flop:** After hole cards are dealt, betting starts with the player to the left of the big blind (or the small blind in heads-up). The big blind has the option to check or raise after all other players have acted.
2. **Flop:** Three community cards are dealt face-up on the table. A new betting round begins, starting with the first active player after the button.
3. **Turn:** A fourth community card is dealt. Another round of betting follows.
4. **River:** The fifth and final community card is dealt. The last round of betting takes place.

After each community card stage, one card is burned (discarded unseen) before dealing, following standard poker protocol.

### Showdown
If two or more players remain after the final betting round, a showdown occurs. Each remaining player reveals their hand, and the player with the best five-card poker hand wins the pot. If multiple players tie, the pot is split equally among them.

When a player is all in and cannot match all bets, side pots are created. Each side pot is awarded independently, meaning a player can only win from a pot they have contributed to.

### Hand Rankings
From strongest to weakest, the ten poker hand rankings are:

1. **Royal Flush:** A, K, Q, J, 10 all of the same suit. The best possible hand.
2. **Straight Flush:** Five consecutive cards of the same suit (e.g., 7, 8, 9, 10, J of hearts).
3. **Four of a Kind:** Four cards of the same rank (e.g., four Kings).
4. **Full House:** Three of a kind plus a pair (e.g., three 8s and two 5s).
5. **Flush:** Five cards of the same suit, not in sequence.
6. **Straight:** Five consecutive cards of mixed suits (e.g., 4, 5, 6, 7, 8). Ace can be high (A, K, Q, J, 10) or low (A, 2, 3, 4, 5), but cannot wrap around (e.g., Q, K, A, 2, 3 is not valid).
7. **Three of a Kind:** Three cards of the same rank.
8. **Two Pair:** Two different pairs (e.g., two Jacks and two 7s).
9. **One Pair:** Two cards of the same rank.
10. **High Card:** When no other hand is made, the highest card plays.

When two hands are of the same rank, the higher cards within that rank break the tie. If those are also equal, kicker cards (the remaining cards in the five-card hand) are compared from highest to lowest.

### Blind Increases
If the blind timer is enabled, blinds increase automatically at set intervals. The multiplier grows through levels: 1x, 2x, 3x, 4x, 5x, 10x, 20x, 30x, 40x, 50x, and 100x the original blind values. The table is notified when blinds are about to increase. This tournament-style structure ensures the game reaches a conclusion as short-stacked players are pressured into action.

### Winning the Game
The game ends when one player has accumulated all the chips. That player is declared the winner.

### Customizable Options
The host can adjust several settings before the game starts:

* **Starting Chips:** The number of chips each player begins with. Defaults to 20,000. Can be set from 100 to 1,000,000.
* **Big Blind:** The size of the big blind. Defaults to 200. The small blind is always half this value (rounded down). Can be set from 1 to 1,000,000.
* **Ante:** An additional forced bet posted by every player before each hand. Defaults to 0 (disabled). Can be set from 0 to 1,000,000.
* **Ante Start Level:** The blind level at which the ante kicks in. Defaults to 0 (ante active immediately if set). Can be set from 0 to 20. This lets you add antes only in the later stages of the game when blinds have already increased.
* **Turn Timer:** How many seconds each player has to act on their turn. Options are 5, 10, 15, 20, 30, 45, 60, or 90 seconds, or unlimited (the default). If time runs out, the player automatically checks (if possible) or folds.
* **Blind Timer:** How many minutes between blind level increases. Options are 5, 10, 15, 20, or 30 minutes. Defaults to 20 minutes.
* **Raise Mode:** Controls the maximum raise size. Options are:
    * *No Limit (default):* Raise any amount up to your entire stack at any time.
    * *Pot Limit:* Raise up to the current size of the pot.
    * *Double Pot Limit:* Raise up to double the current pot size.
* **Max Raises:** The maximum number of raises allowed per betting round. Defaults to 0 (unlimited). Can be set from 0 to 10.

### Example Hand
Six players sit down. Starting chips are 20,000 each. Big blind is 200, small blind is 100.

The button is with Alice. Bob posts the small blind of 100. Carol posts the big blind of 200. Everyone is dealt two hole cards.

Pre-flop betting starts with Dave (the player after the big blind). Dave folds. Eve calls 200. Frank folds. Alice calls 200. Bob calls 100 more (bringing his total to 200). Carol checks (she already has 200 in).

The pot is now 800. The flop comes: 7 of spades, 10 of diamonds, Jack of hearts.

Bob checks. Carol bets 400. Eve folds. Alice calls 400. Bob folds.

The pot is now 1,600. The turn comes: 2 of clubs.

Carol bets 800. Alice raises 1,600 (putting in 2,400 total). Carol calls the additional 1,600.

The pot is now 6,400. The river comes: King of spades.

Carol checks. Alice bets 3,000. Carol folds.

Alice wins the pot of 9,400 without having to show her cards. A new hand begins with the button moving to Bob.

## Keyboard Shortcuts
Shortcuts specific to Texas Hold'em:

* **C:** Call or check (matches the current bet, or checks if there is nothing to call).
* **R:** Raise (you will be prompted to enter a raise amount).
* **F:** Fold.
* **Shift+A:** Go all in.
* **W:** Read your hole cards.
* **E:** Read the community cards on the table.
* **G:** Read your current best hand value (e.g., "pair of Kings" or "flush, Ace high").
* **P:** Check the current pot size.
* **N:** Check the amount you need to call.
* **M:** Check the minimum raise amount.
* **H:** Check which players are still in the hand.
* **X:** Check who has the button.
* **Z:** Check your position relative to the button.
* **V:** Check the blind timer (time until next blind increase).
* **Shift+T:** Check the turn timer (time remaining for the current player's action).
* **1 through 7:** Read a specific card by its position (hole cards first, then community cards).
* **O:** Reveal both of your hole cards to the table (only available at showdown).
* **U:** Reveal your first hole card to the table (only available at showdown).
* **I:** Reveal your second hole card to the table (only available at showdown).
* **S:** Check chip counts for all players.
* **T:** Check whose turn it is.

## Game Theory / Tips
* **Position is everything.** Acting later in a betting round gives you more information about what other players have done. The button is the strongest position because you act last on every post-flop round. If you are in early position, tighten your starting hand selection significantly.
* **Starting hand selection matters more than anything else.** Most hands dealt to you are not worth playing. High pairs (Aces, Kings, Queens), high suited connectors (Ace-King suited, King-Queen suited), and medium-to-high pairs are strong starting hands. Low unsuited cards with no connection to each other are almost always a fold.
* **Pay attention to pot odds.** If you need to call 200 into a pot of 1,000, you are getting 5-to-1 odds. If your chance of completing your hand is better than 1 in 6, the call is mathematically profitable in the long run.
* **Do not slow-play strong hands too often.** Checking and calling with a very strong hand can let opponents draw to better hands for free. Bet for value when you have it.
* **Bluffing works best against fewer opponents.** It is much easier to make one player fold than four. Semi-bluffs (betting with a drawing hand that could improve) are generally safer than pure bluffs.
* **Manage your stack relative to the blinds.** If your chip stack falls below about 10 big blinds, you are in push-or-fold territory: either go all in or fold. There is not enough room for standard raises at that point.
* **Watch the blind timer.** As blinds increase, the value of each chip decreases relative to the forced bets. Do not sit and wait for premium hands if the blinds are eating you alive.
* **Side pots can change who you are competing against.** When a short-stacked player goes all in, a side pot is created for the remaining players. You might lose the main pot but win the side pot, or vice versa. Keep track of who is eligible for which pot.
