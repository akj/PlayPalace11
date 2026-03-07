# Rolling Balls game messages
# Note: Common messages like round-start, turn-start are in games.ftl

# Game info
game-name-rollingballs = Kotrljajuće loptice

# Turn actions
rb-take = Uzmi { $count } { $count ->
    [one] lopticu
    [few] loptice
   *[other] loptica
}
rb-reshuffle-action = Promešaj cev ({ $remaining } korišćenja preostalo)
rb-view-pipe-action = Prikaži cev ({ $remaining } korišćenja preostalo)

# Take ball events
rb-you-take = Uzimate { $count } { $count ->
    [one] lopticu
    [few] loptice
   *[other] loptica
}!
rb-player-takes = { $player } uzima { $count } { $count ->
    [one] lopticu
    [few] loptice
   *[other] loptica
}!
rb-ball-plus = Loptica { $num }: { $description }! Plus { $value } poena!
rb-ball-minus = Loptica { $num }: { $description }! Minus { $value } poena!
rb-ball-zero = Loptica { $num }: { $description }! Bez promene!
rb-new-score = Rezultat igrača { $player }: { $score } poena.

# Reshuffle events
rb-you-reshuffle = Mešate cev!
rb-player-reshuffles = { $player } meša cev!
rb-reshuffled = Cev je promešana!
rb-reshuffle-penalty = { $player } gubi { $points } { $points ->
    [one] poen
   *[other] poena
} zbog mešanja.

# View pipe
rb-view-pipe-header = Ima { $count } loptica:
rb-view-pipe-ball = { $num }: { $description }. Vrednost: { $value } poena.

# Game start
rb-pipe-filled = Cev je popunjena sa { $count } loptica!
rb-balls-remaining = { $count } loptica preostalo u cevi.

# Game end
rb-pipe-empty = Cev je prazna!
rb-score-line = { $player }: { $score } poena.
rb-winner = Pobednik je { $player } sa { $score } poena!
rb-you-win = Pobedili ste sa { $score } poena!
rb-tie = Izjednačeno je između igrača { $players } sa { $score } poena!

# Options
rb-set-min-take = Najmanji broj loptica koji se mora uzeti po potezu: { $count }
rb-enter-min-take = Upišite najmanji broj loptica za uzimanje (1-5):
rb-option-changed-min-take = Najmanji broj loptica za uzimanje podešen na { $count }.

rb-set-max-take = Najveći broj loptica za uzimanje po potezu: { $count }
rb-enter-max-take = Upišite najveći broj loptica za uzimanje (1-5):
rb-option-changed-max-take = Najveći broj loptica za uzimanje podešen na { $count }.

rb-set-view-pipe-limit = Ograničenje prikazivanja cevi: { $count }
rb-enter-view-pipe-limit = Upišite ograničenje prikazivanja cevi (0 da onemogućite, najviše 100):
rb-option-changed-view-pipe-limit = Ograničenje prikazivanja cevi podešeno na { $count }.

rb-set-reshuffle-limit = Ograničenje mešanja: { $count }
rb-enter-reshuffle-limit = Upišite ograničenje mešanja (0 da onemogućite, najviše 100):
rb-option-changed-reshuffle-limit = Ograničenje mešanja podešeno na { $count }.

rb-set-reshuffle-penalty = Kazna za mešanje: { $points }
rb-enter-reshuffle-penalty = Upišite kaznu za mešanje (0-5):
rb-option-changed-reshuffle-penalty = Kazna za mešanje podešena na { $points }.

rb-set-ball-packs = Paketi loptica ({ $count } od { $total } izabrano)
rb-option-changed-ball-packs = Paketi loptica ažurirani ({ $count } od { $total } izabrano).

# Disabled reasons
rb-not-enough-balls = Nema dovoljno loptica u cevi.
rb-no-reshuffles-left = Nema preostalih mešanja.
rb-already-reshuffled = Već ste promešali u ovom potezu.
rb-no-views-left = Nema preostalih prikazivanja cevi.
