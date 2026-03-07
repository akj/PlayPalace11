# Yahtzee game messages

# Game info
game-name-yahtzee = Jamb

# Actions - Rolling
yahtzee-roll = Baci ponovo ({ $count } bacanja preostalo)
yahtzee-roll-all = Baci kockice

# Upper section scoring categories
yahtzee-score-ones = Jedinice  { $points } poena
yahtzee-score-twos = Dvojke { $points } poena
yahtzee-score-threes = Trojke { $points } poena
yahtzee-score-fours = Četvorke { $points } poena
yahtzee-score-fives = Petice { $points } poena
yahtzee-score-sixes = Šestice { $points } poena

# Lower section scoring categories
yahtzee-score-three-kind = Tri iste { $points } poena
yahtzee-score-four-kind = Četiri iste { $points } poena
yahtzee-score-full-house = Ful haus { $points } poena
yahtzee-score-small-straight = Mala kenta { $points } poena
yahtzee-score-large-straight = Velika kenta { $points } poena
yahtzee-score-yahtzee = jamb { $points } poena
yahtzee-score-chance = Šansa { $points } poena

# Game events
yahtzee-you-rolled = Dobili ste: { $dice }. Preostalo bacanja: { $remaining }
yahtzee-player-rolled = { $player } dobija: { $dice }. Preostalo bacanja: { $remaining }

# Scoring announcements
yahtzee-you-scored = Upisali ste { $points } poena u redu { $category }.
yahtzee-player-scored = { $player } upisuje { $points } poena u redu { $category }.

# Yahtzee bonus
yahtzee-you-bonus = Bonus za jamb! +100 poena
yahtzee-player-bonus = { $player } dobija bonus za jamb! +100 poena

# Upper section bonus
yahtzee-you-upper-bonus = Bonus za grupe! +35 poena ({ $total } u grupama)
yahtzee-player-upper-bonus = { $player } dobija bonus za grupe! +35 poena
yahtzee-you-upper-bonus-missed = Izgubili ste bonus za grupe ({ $total } u grupama, neophodno 63).
yahtzee-player-upper-bonus-missed = { $player } gubi bonus za grupe.

# Scoring mode
yahtzee-choose-category = Izaberite red za upisivanje poena.
yahtzee-continuing = Potez se nastavlja.

# Status checks
yahtzee-check-scoresheet = Proveri tabelu rezultata
yahtzee-view-dice = Proveri ruku
yahtzee-your-dice = Vaše kockice: { $dice }.
yahtzee-your-dice-kept = Vaše kockice: { $dice }. Zadržava se: { $kept }
yahtzee-not-rolled = Još uvek niste bacili.

# Scoresheet display
yahtzee-scoresheet-header = Tabela rezultata igrača { $player }
yahtzee-scoresheet-upper = Grupe:
yahtzee-scoresheet-lower = Ostalo:
yahtzee-scoresheet-category-filled = { $category }: { $points }
yahtzee-scoresheet-category-open = { $category }: -
yahtzee-scoresheet-upper-total-bonus = Ukupno u grupama: { $total } (BONUS: +35)
yahtzee-scoresheet-upper-total-needed = Ukupno u grupama: { $total } (još { $needed } neophodno za bonus)
yahtzee-scoresheet-yahtzee-bonus = Bonusi za jamb: { $count } x 100 = { $total }
yahtzee-scoresheet-grand-total = Ukupan rezultat: { $total }

# Category names (for announcements)
yahtzee-category-ones = Jedinice
yahtzee-category-twos = Dvojke
yahtzee-category-threes = Trojke
yahtzee-category-fours = Četvorke
yahtzee-category-fives = Petice
yahtzee-category-sixes = Šestice
yahtzee-category-three-kind = Tri iste
yahtzee-category-four-kind = Četiri iste
yahtzee-category-full-house = Ful haus
yahtzee-category-small-straight = Mala kenta
yahtzee-category-large-straight = Velika kenta
yahtzee-category-yahtzee = Jamb
yahtzee-category-chance = Šansa

# Game end
yahtzee-winner = { $player } pobeđuje sa { $score } poena!
yahtzee-winners-tie = Izjednačeno! { $players } su dobili { $score } poena!

# Options
yahtzee-set-rounds = Broj igara: { $rounds }
yahtzee-enter-rounds = Upišite broj igara (1-10):
yahtzee-option-changed-rounds = Broj igara podešen na { $rounds }.

# Disabled action reasons
yahtzee-no-rolls-left = Nemate više bacanja.
yahtzee-roll-first = Prvo morate da bacite.
yahtzee-category-filled = Taj red je već popunjen.
