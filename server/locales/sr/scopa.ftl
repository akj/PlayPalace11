# Scopa game messages
# Note: Common messages like round-start, turn-start, target-score, team-mode are in games.ftl

# Game name
game-name-scopa = Skopa

# Game events
scopa-initial-table = Karte na stolu: { $cards }
scopa-no-initial-table = Nema karata na stolu na početku.
scopa-you-collect = Uzimate { $cards } kartom { $card }
scopa-player-collects = { $player } uzima { $cards } kartom { $card }
scopa-you-put-down = Stavljate { $card }.
scopa-player-puts-down = { $player } stavlja { $card }.
scopa-scopa-suffix =  - SKOPA!
scopa-clear-table-suffix = , čišćenjem stola.
scopa-remaining-cards = { $player } uzima preostale karte sa stola.
scopa-scoring-round = Računanje runde...
scopa-most-cards = { $player } dobija poen za najviše karata ({ $count } karata).
scopa-most-cards-tie = Najveći broj karata izjednačen - nema  poena.
scopa-most-diamonds = { $player } dobija 1 poen za najviše karoa ({ $count } karoa).
scopa-most-diamonds-tie = Najveći broj karoa izjednačen - nema poena.
scopa-seven-diamonds = { $player } dobija 1 poen za sedmicu karo.
scopa-seven-diamonds-multi = { $player } dobija 1 poen za najviše sedmica karo ({ $count } × 7 karo).
scopa-seven-diamonds-tie = Broj sedmica karo je izjednačen - nema poena.
scopa-most-sevens = { $player } dobija 1 poen za najviše sedmica ({ $count } sedmica).
scopa-most-sevens-tie = Najveći broj sedmica izjednačen - nema poena.
scopa-round-scores = Rezultat runde:
scopa-round-score-line = { $player }: +{ $round_score } (ukupno: { $total_score })
scopa-table-empty = Nema karata na stolu.
scopa-no-such-card = Nema karte na ovoj poziciji.
scopa-captured-count = Uzeli ste { $count } karata

# View actions
scopa-view-table = Pogledaj sto
scopa-view-captured = Pogledaj uzete karte

# Scopa-specific options
scopa-enter-target-score = Upišite krajnji rezultat (1-121)
scopa-set-cards-per-deal = Broj karata po deljenju: { $cards }
scopa-enter-cards-per-deal = Upišite broj karata po deljenju (1-10)
scopa-set-decks = Broj špilova: { $decks }
scopa-enter-decks = Upišite broj špilova (1-6)
scopa-toggle-escoba = Eskoba (zbir 15): { $enabled }
scopa-toggle-hints = Prikaži savete za uzimanje: { $enabled }
scopa-set-mechanic = Mehanizam skope: { $mechanic }
scopa-select-mechanic = Izaberite mehanizam skope
scopa-toggle-instant-win = Automatska pobeda nakon skope: { $enabled }
scopa-toggle-team-scoring = Saberi karte tima pri bodovanju: { $enabled }
scopa-toggle-inverse = Obrnuti režim (dostizanje krajnjeg rezultata=ispadanje): { $enabled }

# Option change announcements
scopa-option-changed-cards = Broj karata po deljenju podešen na { $cards }.
scopa-option-changed-decks = Broj špilova podešen na { $decks }.
scopa-option-changed-escoba = Eskoba { $enabled }.
scopa-option-changed-hints = saveti za uzimanje { $enabled }.
scopa-option-changed-mechanic = Skopa mehanizam podešen na { $mechanic }.
scopa-option-changed-instant = Pobeđivanje odmah nakon skope { $enabled }.
scopa-option-changed-team-scoring = Timsko bodovanje karata { $enabled }.
scopa-option-changed-inverse = Obrnuti režim { $enabled }.

# Scopa mechanic choices
scopa-mechanic-normal = Standardni
scopa-mechanic-no_scopas = Bez skope
scopa-mechanic-only_scopas = Samo skope

# Disabled action reasons
scopa-timer-not-active = Tajmer runde nije aktivan.

# Validation errors
scopa-error-not-enough-cards = Nema dovoljno karata u { $decks } { $decks ->
    [one] špilu
    [few] špila
    *[other] špilova
} za { $players } { $players ->
    [one] igrača
    *[other] igrača
} sa po { $cards_per_deal } karata. (Potrebno vam je { $cards_per_deal } × { $players } = { $cards_needed } karata, ali imate samo { $total_cards }.)
