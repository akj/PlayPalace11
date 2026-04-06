# Rules Of Blackjack
PlayPalace team, 2026.

## TL;DR
Blackjack is the classic casino card game where you try to beat the dealer by getting a hand total as close to 21 as possible without going over. Each player plays independently against the dealer, not against each other. Number cards are worth their face value, face cards are worth 10, and aces count as 11 or 1, whichever helps you more. You start with chips, place bets each hand, and the game continues until only one player has chips remaining, or in solo play, until you go broke.

## Gameplay
The game supports 1 to 7 players. Each player starts with a pool of chips and places a bet before each hand is dealt.

### Betting
Before each hand, you are prompted to place your bet. You can press B to quickly confirm your previous bet, or type a new amount. Your bet must fall within the table minimum and maximum limits. If you do not enter a bet before the timer expires (when a turn timer is active), the base bet is used automatically.

### The Deal
Once all bets are placed, each player and the dealer receive two cards. One of the dealer's cards is face up and announced to the table; the other remains hidden. If the "player cards face up" option is enabled, all players can see each other's cards. Otherwise, you can only see your own.

If your initial two cards total exactly 21 (an ace plus a ten-value card), you have blackjack. This is announced immediately and your hand stands automatically.

### Card Values
- Number cards (2 through 10): face value.
- Face cards (jack, queen, king): 10.
- Aces: count as 11 unless that would push your total over 21, in which case they count as 1. A hand where an ace is actively counting as 11 is called "soft" (for example, an ace and a 6 is "17 soft"). When your total would exceed 21, aces are automatically reduced to 1.

### Insurance and Even Money
When the dealer's face-up card is an ace and insurance is enabled, you are given the opportunity to take insurance or even money before normal play begins.

- Insurance: if you do not have blackjack, you may place a side bet equal to half your original bet. If the dealer turns out to have blackjack, insurance pays 2 to 1. If the dealer does not have blackjack, you lose the insurance bet.
- Even money: if you have blackjack and the dealer shows an ace, you can take even money. This guarantees a 1-to-1 payout on your bet immediately, regardless of whether the dealer also has blackjack.

You can also decline insurance, in which case play continues normally.

### Player Actions
On your turn, you choose from the following actions:

- Hit: draw one more card. If your total exceeds 21, you bust and lose your bet immediately. If your total reaches exactly 21, you stand automatically.
- Stand: keep your current hand and end your turn.
- Double down: double your bet and receive exactly one more card, after which your hand stands automatically. Doubling is only available on your first two cards (before hitting). Depending on the rules profile, doubling may be restricted to hands totaling 9-11 or 10-11.
- Split: if your first two cards are a matching pair, you can split them into two separate hands, each with its own bet equal to your original bet. Each hand receives a second card and is played independently. You play hand 1 first, then hand 2. Depending on the rules profile, pairs must match by rank (two 8s) or by value (a king and a 10 both count as 10). Splitting is limited to one split (2 hands maximum by default).
- Surrender: forfeit half your bet and end the hand immediately. This is only available on your original two cards before hitting, and only when late surrender is enabled. You cannot surrender a split hand or a blackjack.

### Split Aces
Splitting aces has special rules that vary by profile:

- One-card rule: when enabled (Vegas and European profiles), each split ace receives exactly one card and stands automatically. You cannot hit, double down, or take further action.
- Blackjack on split aces: when enabled (Friendly profile), an ace plus a ten-value card on a split hand counts as blackjack and pays the blackjack bonus. When disabled (Vegas and European profiles), this combination is treated as a regular 21.

### Dealer Rules
After all players have acted, the dealer reveals the hidden card. The dealer then follows a fixed rule:

- The dealer must hit on 16 or below.
- Whether the dealer hits or stands on soft 17 (a hand totaling 17 with an ace counting as 11) depends on the rules profile. In the Vegas profile, the dealer hits soft 17. In European and Friendly profiles, the dealer stands on soft 17.
- The dealer stands on hard 17 or above.

If the "dealer peeks for blackjack" option is enabled (Vegas and Friendly profiles), the dealer checks for blackjack when showing an ace (after insurance decisions). If the dealer has blackjack, the hand ends immediately without players taking their turns.

### Settlement
After the dealer finishes, each hand is settled:

- If you have blackjack and the dealer does not, you are paid at the blackjack payout rate (default 3 to 2). On a 10-chip bet, that means 15 chips profit.
- If you bust, you lose your bet regardless of the dealer's result.
- If the dealer busts and you did not, you win even money (1 to 1).
- If neither busted, the higher total wins at even money. Equal totals are a push, and your bet is returned.
- If the dealer has blackjack and you do not, you lose.
- Surrendered hands have already forfeited half the bet and are not settled further.
- Even money hands have already been paid out and are not settled further.
- Insurance bets are settled separately: if the dealer has blackjack, insurance pays 2 to 1. Otherwise, the insurance bet is lost.

### Elimination
When a player runs out of chips, they are eliminated. In multiplayer, the game ends when only one player has chips remaining -- that player wins. In solo play, the game ends when you go broke.

### Customizable Options
The host can configure these settings before the game starts:

* **Rules Profile:** A preset that adjusts multiple rules at once. Choose from Vegas (default), European, or Friendly. You can also change individual rules after selecting a profile.
* **Starting Chips:** How many chips each player begins with. Default 500, range 50 to 1,000,000.
* **Base Bet:** The default bet placed each hand if you do not specify one. Default 10, range 1 to 100,000.
* **Table Minimum Bet:** The lowest bet allowed. Default 5, range 1 to 100,000.
* **Table Maximum Bet:** The highest bet allowed. Default 100, range 1 to 100,000.
* **Deck Count:** Number of standard 52-card decks shuffled together. Default 4, range 1 to 8.
* **Dealer Hits Soft 17:** Whether the dealer must hit on soft 17. Default: yes (Vegas).
* **Dealer Peeks for Blackjack:** Whether the dealer checks for blackjack when showing an ace. Default: yes (Vegas).
* **Player Cards Face Up:** Whether all players can see each other's cards. Default: yes.
* **Insurance and Even Money:** Whether insurance and even money are offered when the dealer shows an ace. Default: yes.
* **Late Surrender:** Whether players can surrender their hand. Default: yes (Vegas).
* **Blackjack Payout:** The bonus payout for a natural blackjack. Options: 3 to 2 (default), 6 to 5, or 1 to 1.
* **Double Down Rule:** When doubling is allowed. Options: any two cards (default), totals 9 to 11, or totals 10 to 11.
* **Double After Split:** Whether you can double down on a split hand. Default: yes (Vegas).
* **Split Rule:** What constitutes a pair for splitting. Options: same rank (default, e.g. two 8s), or same value (e.g. king and 10 both worth 10).
* **Maximum Split Hands:** How many hands you can split into. Default 2, range 1 to 2. Set to 1 to disable splitting entirely.
* **Split Aces One Card Only:** Whether split aces receive just one card each. Default: yes (Vegas).
* **Split Aces Count as Blackjack:** Whether an ace plus a ten-value card on a split hand pays the blackjack bonus. Default: no (Vegas).
* **Turn Timer:** Optional time limit per decision. Options: 5, 10, 15, 20, 30, 45, 60, or 90 seconds, or unlimited (default). When the timer expires, the game automatically plays for you (standing on your current total, or declining insurance).

### Rules Profiles at a Glance
- **Vegas:** Dealer hits soft 17, peeks for blackjack, insurance on, late surrender on, 3 to 2 blackjack payout, double on any two cards, double after split allowed, split by rank, split aces get one card, split aces do not count as blackjack.
- **European:** Dealer stands on soft 17, no peek, insurance on, no late surrender, 3 to 2 payout, double on 9-11 only, no double after split, split by rank, split aces get one card, split aces do not count as blackjack.
- **Friendly:** Dealer stands on soft 17, peeks for blackjack, insurance on, late surrender on, 3 to 2 payout, double on any two cards, double after split allowed, split by value, split aces can hit freely, split aces count as blackjack.

### Example Turn
You have 500 chips and the base bet is 10. The hand starts and 10 chips are deducted from your stack.

The dealer shows a 7 of spades. You are dealt a 5 of hearts and a 6 of diamonds, giving you a total of 11. This is a great doubling opportunity.

You press D to double down. Another 10 chips are deducted (your bet is now 20) and you receive exactly one card: a 9 of clubs. Your total is 20 and your hand stands automatically.

The dealer reveals a jack of hearts (hidden card) for a total of 17. The dealer stands on 17.

Your 20 beats the dealer's 17. You win 20 chips, bringing your stack to 510.

## Keyboard Shortcuts
Shortcuts specific to Blackjack:

* Space: Hit (draw a card).
* X: Stand (keep your hand).
* D: Double down.
* P: Split your pair.
* U: Surrender.
* B: Change your bet (between hands) or read current bets (during a hand).
* I: Take insurance.
* N: Decline insurance.
* M: Take even money.
* R: Read your hand and total.
* C: Read the dealer's visible card or full hand.
* E: Table status (all players' chips, bets, and totals).
* Shift+R: Read the current rules configuration.
* T: Check whose turn it is.
* S: Check scores (chip counts).
* Shift+S: Detailed scores.
* Shift+T: Check turn timer remaining.

## Game Theory / Tips
* Basic strategy charts exist for blackjack and are well worth learning. The optimal play depends on your hand total and the dealer's up card. As a starting point: always hit on 11 or below, always stand on hard 17 or above, and double down on 11 against a dealer 2 through 10.
* Never take insurance. Mathematically, insurance is a losing bet in the long run. The only exception is if you are counting cards and know the deck is rich in tens, which is less effective with multiple decks anyway.
* Even money is mathematically equivalent to taking insurance when you have blackjack. It guarantees a 1-to-1 payout instead of the usual 3-to-2. Most strategy guides recommend declining even money for the same reason they recommend declining insurance: the expected value is higher without it.
* When to double down: the classic spots are hard 11 (always double), hard 10 (double unless the dealer shows a 10 or ace), and hard 9 (double against dealer 3 through 6). With soft hands, double on soft 13 through 17 against dealer 4 through 6.
* When to split: always split aces and 8s. Never split 10s or 5s. Split 2s, 3s, 6s, and 7s against dealer 2 through 7. Split 4s only against dealer 5 or 6 (if double after split is allowed). Split 9s against everything except 7, 10, or ace.
* Surrender is a powerful tool when available. Surrender hard 16 against a dealer 9, 10, or ace. Surrender hard 15 against a dealer 10.
* With more decks in the shoe, the house edge increases slightly. Fewer decks favor the player, all else being equal.
* The dealer hitting on soft 17 increases the house edge by about 0.2%. If you have the choice, prefer profiles where the dealer stands on soft 17.
* Pay attention to the blackjack payout setting. A 6-to-5 payout roughly doubles the house edge compared to 3-to-2. Avoid 6-to-5 games if possible.
* In multiplayer, remember that you are not competing against other players directly. Each player independently tries to beat the dealer. However, the last player standing wins, so chip management matters. Do not bet so aggressively that a few bad hands eliminate you while cautious opponents survive.
