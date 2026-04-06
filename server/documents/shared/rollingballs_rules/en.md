# Rules Of Rolling Balls
PlayPalace team, 2026.

## TL;DR
Rolling Balls is a push-your-luck pipe game for 2 to 4 players. A pipe is filled with balls, each carrying a hidden point value between -5 and +5 along with a flavor description. On your turn, you choose how many balls to pull from the front of the pipe (between 1 and 3 by default). Their values are added to your score, for better or worse. You can peek at the pipe's contents or reshuffle it to dodge bad balls, but both of those abilities are limited. When the pipe runs out, whoever has the most points wins.

## Gameplay
The game is divided into rounds. In each round, every player takes one turn in order.

At the start of the game, the pipe is filled with balls drawn randomly from the active ball packs. The number of balls depends on the player count: 25 balls for 2 players, 35 for 3, and 50 for 4. Each ball has a point value (ranging from -5 to +5) and a descriptive name that is announced when you pull it.

On your turn, you choose how many balls to take from the front of the pipe. By default you can take 1, 2, or 3 balls (configurable by the host). The balls are revealed one at a time with sound and speech: positive balls add to your score, negative balls subtract from it, and zero-value balls do nothing. After all your balls are revealed, your updated score is announced and play passes to the next player.

You also have two special abilities you can use on your turn before taking balls:

**View Pipe:** Privately peek at the entire contents of the pipe, seeing every ball's name and point value in order. This does not cost your turn. You have a limited number of uses per game (5 by default). Viewing the pipe again without the pipe having changed does not consume an additional use.

**Reshuffle:** Shuffle the first 15 balls in the pipe (or all remaining balls if fewer than 15 are left) into a random order. This can save you from a string of negative balls at the front, but it costs a point penalty (1 point by default) and you can only reshuffle once per turn. You have a limited number of reshuffles per game (3 by default). Reshuffling requires at least 6 balls remaining in the pipe.

If fewer balls remain than the minimum take amount, those balls are automatically taken by the current player.

The game ends as soon as the pipe is empty. The player with the highest score wins. In the event of a tie, the tied players share the victory.

### Customizable Options
The host can adjust several settings before the game starts:

* **Minimum Balls to Take:** The fewest balls you must take per turn. Defaults to 1, range 1 to 5.
* **Maximum Balls to Take:** The most balls you can take per turn. Defaults to 3, range 1 to 5. If set lower than the minimum, the minimum is adjusted down automatically, and vice versa.
* **View Pipe Limit:** How many times each player can view the pipe during the game. Defaults to 5. Set to 0 to disable pipe viewing entirely. Maximum 100.
* **Reshuffle Limit:** How many times each player can reshuffle during the game. Defaults to 3. Set to 0 to disable reshuffling entirely. Maximum 100.
* **Reshuffle Penalty:** How many points are deducted each time you reshuffle. Defaults to 1, range 0 to 5. This option is only visible when reshuffling is enabled.
* **Ball Packs:** Which themed sets of balls to include in the pipe. At least one pack must be selected. Available packs include "Rory's Pack" (programming-themed) and "Pizza" (pizza-themed), among others. Multiple packs can be active at once, and balls are drawn randomly from the combined pool.

### Example Turn
You are playing a 2-player game. The pipe has 18 balls remaining. Your score is 7 and your opponent's score is 12.

You decide to view the pipe first. You see that the first three balls are: "Tiny bug" (value -1), "Silva's pizza arrives" (value +3), and "Epic win" (value +4). That is a net of +6 if you take all three, but you would eat the -1 first.

You could reshuffle to try to push the negative ball further back, but the +3 and +4 right behind it are too good to risk losing. You decide to take 3 balls.

Ball 1: Tiny bug! Minus 1 point. Ball 2: Silva's pizza arrives! Plus 3 points. Ball 3: Epic win! Plus 4 points.

Your score is now 13, putting you one point ahead. Play passes to your opponent.

## Keyboard Shortcuts
Shortcuts specific to Rolling Balls:

* 1: Take 1 ball.
* 2: Take 2 balls.
* 3: Take 3 balls.
* 4: Take 4 balls (if maximum take is set to 4 or higher).
* 5: Take 5 balls (if maximum take is set to 5).
* D: Reshuffle the pipe.
* P: View the pipe.
* S: Check scores.
* Shift+S: View detailed scores.

## Game Theory / Tips
* Viewing the pipe is your most powerful tool. Use it wisely. If the pipe has not changed since your last view (no one has taken or reshuffled), viewing again is free. Try to view right after an opponent reshuffles or takes balls so you get fresh information.
* Reshuffling is a defensive move. If you peek at the pipe and see a cluster of negative balls at the front, reshuffling can scatter them. But remember it costs a point and you can only do it once per turn, so do not waste reshuffles on mild negatives.
* Taking more balls is not always better. If you can see the pipe and the first ball is worth +4 but the second is worth -5, just take 1. The flexibility in how many you take is the core of the strategy.
* Pay attention to the ball count. When few balls remain, the game is about to end. If you are behind, you may need to take the maximum and hope for the best. If you are ahead, taking the minimum reduces your exposure to negative values.
* The pipe is shared. When you take balls, you are also removing them from what your opponents will face. Sometimes taking a bad ball now means your opponent gets an even worse sequence, or vice versa.
* Ball packs have a roughly even distribution from -5 to +5, with equal numbers of positive and negative balls plus a few zeros. Over many balls the expected value trends toward zero, so the game is won on the margins: avoiding the worst negatives and capturing the best positives.
* If reshuffling is disabled or you have used all your reshuffles, your only option when facing bad balls is to take the minimum and move on. Conserve reshuffles for when you see truly devastating sequences at the front of the pipe.
