# Tradeoff game messages

# Game info
game-name-tradeoff = Razmena

# Round and iteration flow
tradeoff-round-start = Runda { $round }.
tradeoff-iteration = Ruka { $iteration } od 3.

# Phase 1: Trading
tradeoff-you-rolled = Dobili ste: { $dice }.
tradeoff-toggle-trade = { $value } ({ $status })
tradeoff-trade-status-trading = Razmena
tradeoff-trade-status-keeping = Zadržavanje
tradeoff-confirm-trades = Potvrdi razmenu ({ $count } kockice)
tradeoff-keeping = Zadržava se { $value }.
tradeoff-trading = Razmenjuje se { $value }.
tradeoff-player-traded = { $player } razmenjuje: { $dice }.
tradeoff-player-traded-none = { $player } zadržava sve kockice.

# Phase 2: Taking from pool
tradeoff-your-turn-take = Vi ste na redu za uzimanje kockice iz gomile.
tradeoff-take-die = Uzmi { $value } ({ $remaining } preostalo)
tradeoff-you-take = Uzimate { $value }.
tradeoff-player-takes = { $player } uzima { $value }.

# Phase 3: Scoring
tradeoff-player-scored = { $player } ({ $points } poena): { $sets }.
tradeoff-no-sets = { $player }: nema skupova.

# Set descriptions (concise)
tradeoff-set-triple = Tri puta { $value }
tradeoff-set-group = Grupa { $value }
tradeoff-set-mini-straight = mini kenta { $low }-{ $high }
tradeoff-set-double-triple = Dva puta po tri iste ({ $v1 } i { $v2 })
tradeoff-set-straight = Kenta { $low }-{ $high }
tradeoff-set-double-group = Dvostruka grupa ({ $v1 } i { $v2 })
tradeoff-set-all-groups = Sve grupe
tradeoff-set-all-triplets = Sve tri iste

# Round end
tradeoff-round-scores = Rezultati runde { $round }:
tradeoff-score-line = { $player }: +{ $round_points } (ukupno: { $total })
tradeoff-leader = { $player } vodi sa rezultatom { $score }.

# Game end
tradeoff-winner = { $player } pobeđuje sa { $score } poena!
tradeoff-winners-tie = Izjednačeno! { $players } imaju { $score } poena!

# Status checks
tradeoff-view-hand = Pogledaj svoju ruku
tradeoff-view-pool = Pogledaj gomilu
tradeoff-view-players = Pogledaj igrače
tradeoff-hand-display = Vaša ruka ({ $count } kockice): { $dice }
tradeoff-pool-display = Gomila ({ $count } kockica): { $dice }
tradeoff-player-info = { $player }: { $hand }. Razmenjeno: { $traded }.
tradeoff-player-info-no-trade = { $player }: { $hand }. Bez razmena.

# Error messages
tradeoff-not-trading-phase = Niste u fazi razmene.
tradeoff-not-taking-phase = Niste u fazi uzimanja.
tradeoff-already-confirmed = Već je potvrđeno.
tradeoff-no-die = Nema kockice za uzimanje ili vraćanje.
tradeoff-no-more-takes = Ništa nije dostupno za uzimanje.
tradeoff-not-in-pool = Ta kockica nije u gomili.

# Options
tradeoff-set-target = Krajnji rezultat: { $score }
tradeoff-enter-target = Upišite krajnji rezultat:
tradeoff-option-changed-target = Krajnji rezultat podešen na { $score }.
