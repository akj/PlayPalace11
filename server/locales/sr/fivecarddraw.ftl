# Five Card Draw

game-name-fivecarddraw = Poker sa pet karata

draw-set-starting-chips = Početni žetoni: { $count }
draw-enter-starting-chips = Upišite početne žetone
draw-option-changed-starting-chips = Početni žetoni podešeni na { $count }.

draw-set-ante = Minimalni ulog: { $count }
draw-enter-ante = Upišite količinu minimalnog uloga
draw-option-changed-ante = Minimalni ulog podešen na { $count }.

draw-set-turn-timer = Tajmer za potez: { $mode }
draw-select-turn-timer = Izaberite tajmer za potez
draw-option-changed-turn-timer = Tajmer za potez podešen na { $mode }.

draw-set-raise-mode = Režim povećavanja uloga: { $mode }
draw-select-raise-mode = Izaberite režim povećavanja uloga
draw-option-changed-raise-mode = Režim povećavanja uloga podešen na { $mode }.

draw-set-max-raises = Maksimum povećavanja uloga: { $count }
draw-enter-max-raises = Upišite maksimum povećavanja uloga (0 za neograničeno)
draw-option-changed-max-raises = Maksimum povećavanja uloga podešen na { $count }.

draw-antes-posted = Minimalan ulog: { $amount }.
draw-betting-round-1 = Runda ulaganja.
draw-betting-round-2 = Runda ulaganja.
draw-begin-draw = Faza izvlačenja.
draw-not-draw-phase = Nije vreme za izvlačenje.
draw-not-betting = Ne možete da ulažete tokom faze izvlačenja.

draw-toggle-discard = Odbaci ili zadrži kartu { $index }
draw-card-keep = { $card }, zadržava se
draw-card-discard = { $card }, odbacuje se
draw-card-kept = Zadrži { $card }.
draw-card-discarded = Odbaci { $card }.
draw-draw-cards = Izvuci karte
draw-draw-cards-count = Izvuci { $count } { $count ->
    [one] kartu
   *[other] karte
}
draw-dealt-cards = Dobili ste { $cards }.
draw-you-drew-cards = Vučete { $cards }.
draw-you-draw = Vučete { $count } { $count ->
    [one] kartu
   *[other] karte
}.
draw-player-draws = { $player } vuče { $count } { $count ->
    [one] kartu
   *[other] karte
}.
draw-you-stand-pat = Ostajete na istom.
draw-player-stands-pat = { $player } ostaje na istom.
draw-you-discard-limit = Možete da odbacite do { $count } karte.
draw-player-discard-limit = { $player } može da odbaci do { $count } karte.
