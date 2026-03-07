# Messages for Left Right Center (English)

# Game name
game-name-leftrightcenter = Levo, desno, centar

# Actions
lrc-roll = Baci { $count } { $count ->
    [one] kockicu
   *[other] kockice
}

# Dice faces
lrc-face-left = Levo
lrc-face-right = Desno
lrc-face-center = Centar
lrc-face-dot = Tačka

# Game events
lrc-roll-results = { $player } dobija { $results }.
lrc-pass-left = { $player } prosleđuje { $count } { $count ->
    [one] žeton
   *[other] žetona
} igraču { $target }.
lrc-pass-right = { $player } prosleđuje { $count } { $count ->
    [one] žeton
   *[other] žetona
} igraču { $target }.
lrc-pass-center = { $player } stavlja { $count } { $count ->
    [one] žeton
   *[other] žetona
} na centar.
lrc-no-chips = { $player } nema žetona za bacanje.
lrc-center-pot = { $count } { $count ->
    [one] žeton
   *[other] žetona
} na centru.
lrc-player-chips = { $player } sada ima { $count } { $count ->
    [one] žeton
   *[other] žetona
}.
lrc-winner = { $player } pobeđuje sa { $count } { $count ->
    [one] žetonom
   *[other] žetona
}!

# Options
lrc-set-starting-chips = Početni žetoni: { $count }
lrc-enter-starting-chips = Upišite početne žetone:
lrc-option-changed-starting-chips = Početni žetoni podešeni na { $count }.
