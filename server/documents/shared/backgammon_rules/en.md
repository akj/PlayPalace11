# Rules Of Backgammon
PlayPalace team, 2026.

## TL;DR
Modern Backgammon (the rules of which were formalized in the 1800s) is a two-player board game with a very long history. It is thought that the first similar games may be more than 4500 years old.

In a game of Backgammon, players take turns rolling the two dice, racing their checkers to their home board and eventually removing them (bearing them off). The winner is the first player to bear off all their checkers.

Series of games (called matches) are preferred in tournaments, because a longer match tends to favour the more skilled player: the luck of the dice mean that in  a single game, a master will lose to a beginner about 25% of the time. Compare this to Chess, in which a beginner will almost never win against a high-level player.

## Gameplay

### Setup
Each player starts with 15 checkers arranged in the standard backgammon opening position:
* 2 checkers on your 24-point
* 5 checkers on your 13-point
* 3 checkers on your 8-point
* 5 checkers on your 6-point

One player is assigned Red and the other White. Colors are assigned randomly at the start of the match.

### Opening Roll
To determine who goes first, each player rolls one die. The player who rolls higher goes first, using both dice (their own die and their opponent's) as their opening roll. If both players roll the same number, they re-roll until someone wins.

### Moving Checkers
On your turn, you roll two dice by pressing Enter on any board point. You then move your checkers according to the dice:
* Each die is a separate move. If you roll a 4 and a 2, you move one checker 4 points forward and one checker (or the same checker) 2 points forward. You cannot combine them into a single move of 6.
* If you roll doubles (both dice show the same number), you get four moves of that number instead of two.
* You must use both dice if possible, but sometimes you may only be able to use one of them. If you cannot move at all, you lose your turn.

To make a move, first select the point your checker is on (this picks it up), then select the destination point (this places it). The game automatically matches your move to the correct die.

### Direction of Movement
You and your opponent race in opposite directions around the board. The board is shown from your perspective: your home area (where you bear off checkers) is in the bottom-right corner, with points numbered 1 through 6. Your opponent's home area is in the top-right corner; from your perspective, those are points 19 through 24, the farthest from your home.

The numbering follows a horseshoe shape, like the letter U turned on its side. Points 1-6 run along the bottom-right, 7-12 continue along the bottom-left, 13-18 pick up at the top-left, and 19-24 finish at the top-right. So moving from point 13 to point 12 doesn't mean jumping diagonally across the board — it's simply moving down from the top-left to the bottom-left, around the bend of the horseshoe.

### Landing Rules
* You can land on any empty point.
* You can land on a point occupied by your own checkers (stacking).
* You can land on a point occupied by exactly one opposing checker. This is called a hit -- the opposing checker is sent to the bar and must re-enter before any other moves can be made.
* You cannot land on a point occupied by two or more opposing checkers. That point is blocked.

### The Bar
When one of your checkers is hit, it goes to the bar. You must re-enter that checker before making any other moves. To re-enter, you need to roll a number corresponding to an open point in your opponent's home board (points 19-24 from your perspective). If you have checkers on the bar and cannot enter, your entire turn is forfeit.

When you have a checker on the bar, simply select any destination point and the game will automatically move from the bar.

### Bearing Off
Once all 15 of your checkers are in your home board, points 1 through 6, you can start bearing them off. To bear off a checker, select it and then select the same point again (press the enter key twice). The game handles the rest.

Bearing-off rules:
* You can bear off a checker from a point that exactly matches a die roll. For example, a roll of 3 lets you bear off from the 3-point.
* If you roll a number higher than your highest occupied point, you can bear off from that highest point. For example, if your highest checker is on the 4-point and you roll a 6, you can bear off from the 4-point.
* You cannot bear off with an overshooting die if there are checkers on higher points. For instance, you cannot bear off from the 3-point with a 5 if you still have checkers on the 4-point or 5-point.
* If a checker is hit during bearing off, it must go to the bar, re-enter, and travel all the way back to the home board before you can resume bearing off.

### Winning a Game
The first player to bear off all 15 checkers wins the game. The number of points scored depends on the loser's position:
* Single (1 point): The loser has borne off at least one checker.
* Gammon (2 points): The loser has not borne off any checkers.
* Backgammon (3 points): The loser has not borne off any checkers and still has checkers on the bar or in the winner's home board.

These point values are multiplied by the current value of the doubling cube.

### The Doubling Cube
In match play (match length greater than 1), the doubling cube adds a strategic dimension. The cube starts centered at 1, meaning either player may offer a double.

Before rolling on your turn, you may offer to double the stakes by pressing Shift+D. Your opponent must then either accept (Y key) or drop (N key):
* If they accept, the cube value doubles (1 to 2, 2 to 4, 4 to 8, and so on), and they gain ownership of the cube. Only the player who owns the cube may offer the next double.
* If they drop, you win the current game immediately, scoring the current cube value in points.

The doubling cube is not available in single games (match length of 1).

### The Crawford Rule
In match play, the Crawford rule applies. When one player is exactly one point away from winning the match, the next game is the Crawford game, during which neither player may use the doubling cube. After the Crawford game, doubling is once again permitted for all subsequent games.

### Match Play
A match consists of multiple games played to a target score. After each game, the winner's points are added to their match score. The first player to reach or exceed the target match length wins the match. Colors are kept throughout the match, but a new opening roll determines who goes first in each game. The doubling cube resets to centered at 1 for each new game.

### Customizable Options
The host can configure the following settings before the game starts:

* **Match Length:** The number of points needed to win the match. Defaults to 1 (a single game with no doubling cube). Can be set from 1 to 25.
* **Bot Difficulty:** The AI difficulty level when playing against a bot. Defaults to Simple. Options are:
    * Random: The bot makes completely random legal moves.
    * Simple: The bot uses basic heuristics (algorithmic, no engine).
    * GNUBG 0-ply: Uses the GNUBG engine with no lookahead (instant evaluation).
    * GNUBG 1-ply: Uses the GNUBG engine with 1-ply lookahead (stronger, slightly slower).
    * GNUBG 2-ply: Uses the GNUBG engine with 2-ply lookahead (strongest, slower).
    Note: There is another difficulty level which we have chosen not to document. You may find it...interesting.

* **Verbose Commentary:** When enabled, move announcements include extra detail. Defaults to off.
* **Hints:** When enabled, you can request move suggestions during your turn. Defaults to off.
* **Cube Hints:** When enabled, you can request doubling advice before rolling or when facing a double. Defaults to off. Only useful in match play.

### Example Turn
It is your turn. You are Red, and you currently have a checker on the bar.

You press Enter on any point to roll. You get a 3 and a 5.

Because you have a checker on the bar, you must re-enter it first. You select point 22 (which is 3 points into your opponent's home board). Your bar checker enters on point 22. The 3 die is used.

Now you select a checker on point 13 and then select point 8. Your checker moves from point 13 to point 8, using the 5 die. Your turn is complete and play passes to your opponent.

## Keyboard Shortcuts
Shortcuts specific to the game of Backgammon:

* **Enter (on any grid point):** Roll dice (before rolling) or select/move a checker (during movement).
* **Ctrl+Backspace:** Deselect the currently selected checker.
* **Ctrl+Arrow (Up/Down/Left/Right):** Cycle between navigation targets. With a checker selected, cycles between available destinations (blots first). Without a selection, cycles between source points that have legal moves.
* **Alt+Arrow:** Jump to the edge of the current grid row or column (left/right for row edges, up/down for column edges).
* **Home / End:** Equivalent to Alt+Left / Right.
* **Shift+D:** Offer to double the stakes (match play only, before rolling).
* **Y:** Accept an opponent's double.
* **N:** Drop (decline) an opponent's double.
* **U:** Undo your last sub-move within the current turn.
* **H:** Request a move hint (must be enabled in options).
* **Shift+H:** Request a cube hint (must be enabled in options, match play only).
* **E:** Check game status (bar and borne-off counts).
* **D:** Check the doubling cube status.
* **P:** Check pip counts for both players.
* **S:** Check match score.
* **C:** Check remaining dice for this turn.
* **T:** Check whose turn it is.

## Game Theory / Tips
* **The opening moves matter.** Certain opening rolls have well-established best plays that have been studied for centuries. For instance, a 3-1 opening is almost always best played by making your 5-point (moving from 8 to 5 and from 6 to 5). Making points, especially in your home board, is a core strategic goal.
* **Build a prime.** A prime is a row of six consecutive blocked points. An opposing checker trapped behind a full prime cannot escape until you break it. Even partial primes of 4 or 5 points in a row are extremely powerful.
* **Hit when it helps, not just because you can.** Sending an opponent to the bar is often strong, but hitting in your own home board when your position is weak can backfire. Consider whether the hit improves your position or just scatters your checkers.
* **Know when to run.** If you have a checker deep in your opponent's territory, sometimes the best play is to run it out early rather than risk it being trapped behind a prime.
* **Bearing off efficiently.** When bearing off, use large dice to clear high points first. Avoid leaving gaps that waste pips. If your opponent still has a back game or checkers in your home board, be cautious about leaving blots (single checkers).
* **The doubling cube is about match equity.** In match play, consider the score before doubling. If you are ahead, you may want to play conservatively with the cube. If you are behind, an early double puts pressure on your opponent and gives you a way to catch up quickly.
* **Crawford game strategy.** In the game immediately after Crawford, the trailing player should often double immediately, since they have nothing to lose.
* **Pip count awareness.** Press P at any time to check pip counts. If you are ahead in the pip count, you generally want to avoid complications and race. If you are behind, you want to create contact and hitting opportunities.
* **learn and train with hints.** If you're playing for practice, enable hints and use them liberally. My strategy is to think about what move I would make until I'm certain, then compare it with the hint. Set your difficulty to GNUBG 2-ply for this.