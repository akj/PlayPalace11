# Toss Up game messages
# Note: Common messages like round-start, turn-start, target-score are in games.ftl

# Game info
game-name-tossup = Semafori
tossup-category = Igre sa kockicama

# Actions
tossup-roll-first = Baci { $count } kockica
tossup-roll-remaining = Baci { $count } preostalih kockica
tossup-bank = Sačuvaj { $points } poena

# Game events
tossup-turn-start = { $player } je na potezu. Rezultat: { $score }
tossup-you-roll = Dobili ste: { $results }.
tossup-player-rolls = { $player } dobija: { $results }.

# Turn status
tossup-you-have-points = Poeni u ovom potezu: { $turn_points }. Preostalo kockica: { $dice_count }.
tossup-player-has-points = { $player } ima { $turn_points } poena u ovom potezu. { $dice_count } kockica preostalo.

# Fresh dice
tossup-you-get-fresh = Nema preostalih kockica! Dobijate { $count } svežih kockica.
tossup-player-gets-fresh = { $player } dobija { $count } svežih kockica.

# Bust
tossup-you-bust = Šteta! Gubite { $points } poena u ovom potezu.
tossup-player-busts = { $player } gubi { $points } poena!

# Bank
tossup-you-bank = Čuvate { $points } poena. Ukupan rezultat: { $total }.
tossup-player-banks = { $player } čuva { $points } poena. Ukupan rezultat: { $total }.

# Winner
tossup-winner = { $player } pobeđuje sa { $score } poena!
tossup-tie-tiebreaker = Izjednačeno između igrača { $players}}! Odlučujuća runda!

# Options
tossup-set-rules-variant = Varijanta pravila: { $variant }
tossup-select-rules-variant = Izaberite varijantu pravila:
tossup-option-changed-rules = Varijanta pravila podešena na { $variant }

tossup-set-starting-dice = Broj početnih kockica: { $count }
tossup-enter-starting-dice = Upišite broj početnih kockica:
tossup-option-changed-dice = Broj početnih kockica podešen na { $count }

# Rules variants
tossup-rules-standard = Standardna
tossup-rules-playpalace = PlayPalace

# Rules explanations
tossup-rules-standard-desc = 3 zelene, 2 žute, 1 crvena po kockici. Poeni se gube ako nema zelenih i postoji bar jedna crvena.
tossup-rules-playpalace-desc = Jednako deljenje. Poeni se gube ako su sve kockice crvene.

# Disabled reasons
tossup-need-points = Morate imati poene za čuvanje.
