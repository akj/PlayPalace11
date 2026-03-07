# Age of Heroes game messages
# A civilization-building card game for 2-6 players

# Game name
game-name-ageofheroes = Doba heroja

# Tribes
ageofheroes-tribe-egyptians = Egipćani
ageofheroes-tribe-romans = Rimljani
ageofheroes-tribe-greeks = Grci
ageofheroes-tribe-babylonians = Vavilonci
ageofheroes-tribe-celts = Kelti
ageofheroes-tribe-chinese = Kinezi

# Special Resources (for monuments)
ageofheroes-special-limestone = Krečnjak
ageofheroes-special-concrete = Beton
ageofheroes-special-marble = Mermer
ageofheroes-special-bricks = Cigle
ageofheroes-special-sandstone = Peščara
ageofheroes-special-granite = Granit

# Standard Resources
ageofheroes-resource-iron = Gvožđe
ageofheroes-resource-wood = Drvo
ageofheroes-resource-grain = Zrno
ageofheroes-resource-stone = Kamen
ageofheroes-resource-gold = Zlato

# Events
ageofheroes-event-population-growth = Rast stanovništva
ageofheroes-event-earthquake = Zemljotres
ageofheroes-event-eruption = Erupcija
ageofheroes-event-hunger = Glad
ageofheroes-event-barbarians = Varvari
ageofheroes-event-olympics = Olimpijske igre
ageofheroes-event-hero = Heroj
ageofheroes-event-fortune = Sreća

# Buildings
ageofheroes-building-army = Vojska
ageofheroes-building-fortress = Tvrđava
ageofheroes-building-general = General
ageofheroes-building-road = Put
ageofheroes-building-city = Grad

# Actions
ageofheroes-action-tax-collection = Porezi
ageofheroes-action-construction = Izgradnja
ageofheroes-action-war = Rat
ageofheroes-action-do-nothing = Ništa
ageofheroes-play = Igraj

# War goals
ageofheroes-war-conquest = Osvajanje
ageofheroes-war-plunder = Pljačka
ageofheroes-war-destruction = Uništenje

# Game options
ageofheroes-set-victory-cities = Broj gradova za pobedu: { $cities }
ageofheroes-enter-victory-cities = Upišite broj gradova za pobedu (3-7)
ageofheroes-set-victory-monument = Popunjenost spomenika: { $progress }%
ageofheroes-toggle-neighbor-roads = Putevi samo sa susedima: { $enabled }
ageofheroes-set-max-hand = Maksimalna veličina ruke: { $cards } karata

# Option change announcements
ageofheroes-option-changed-victory-cities = Pobeda zahteva { $cities } gradova.
ageofheroes-option-changed-victory-monument = Popunjenost spomenika podešena na { $progress }%.
ageofheroes-option-changed-neighbor-roads = Putevi samo sa susedima { $enabled }.
ageofheroes-option-changed-max-hand = Maksimalna veličina ruke podešena na { $cards } karata.

# Setup phase
ageofheroes-setup-start = Vi ste vođa plemena { $tribe }. Resurs vašeg spomenika je { $special }. Bacite kockice kako bi se odredio redosled poteza.
ageofheroes-setup-viewer = Igrači bacaju kockice kako bi se odredio redosled poteza.
ageofheroes-roll-dice = Bacite kockice
ageofheroes-war-roll-dice = Bacite kockice
ageofheroes-dice-result = Dobili ste { $total } ({ $die1 } + { $die2 }).
ageofheroes-dice-result-other = { $player } dobija { $total }.
ageofheroes-dice-tie = Više igrača je dobilo  { $total }. Bacamo ponovo...
ageofheroes-first-player = { $player } je dobio najveći rezultat { $total } i igra prvi!
ageofheroes-first-player-you = Sa { $total } poena, igrate prvi!

# Preparation phase
ageofheroes-prepare-start = Igrači moraju da igraju karte događaja i odbace karte katastrofe.
ageofheroes-prepare-your-turn = Imate { $count } { $count ->
    [one] kartu
    [few] karte
    *[other] karata
} za igranje ili odbacivanje.
ageofheroes-prepare-done = Priprema završena.

# Events played/discarded
ageofheroes-population-growth = { $player } igra rast stanovništva i gradi novi grad.
ageofheroes-population-growth-you = Igrate rast stanovništva i gradite novi grad.
ageofheroes-discard-card = { $player } odbacuje { $card }.
ageofheroes-discard-card-you = Odbacujete { $card }.
ageofheroes-earthquake = Zemljotres pogađa pleme igrača { $player }; njihove vojske se oporavljaju.
ageofheroes-earthquake-you = Zemljotres pogađa vaše pleme; vaše vojske se oporavljaju.
ageofheroes-eruption = Erupcija uništava jedan grad igrača { $player }.
ageofheroes-eruption-you = Erupcija uništava jedan  vaš grad.

# Disaster effects
ageofheroes-hunger-strikes = Glad!
ageofheroes-lose-card-hunger = Gubite { $card }.
ageofheroes-barbarians-pillage = Varvari napadaju resurse igrača { $player }.
ageofheroes-barbarians-attack = Varvari napadaju resurse igrača { $player }!
ageofheroes-barbarians-attack-you = Varvari vas napadaju!
ageofheroes-lose-card-barbarians = Gubite { $card }.
ageofheroes-block-with-card = { $player } sprečava katastrofu kartom { $card }.
ageofheroes-block-with-card-you = Sprečavate katastrofu kartom { $card }.

# Targeted disaster cards (Earthquake/Eruption)
ageofheroes-select-disaster-target = Izaberite protivnika za kartu { $card }.
ageofheroes-no-targets = Nema dostupnih protivnika.
ageofheroes-earthquake-strikes-you = { $attacker } igra zemljotres protiv vas. Vaše vojske se oporavljaju.
ageofheroes-earthquake-strikes = { $attacker } igra zemljotres protiv igrača { $player }.
ageofheroes-armies-disabled = { $count } { $count ->
    [one] vojska se oporavlja na jedan potez.
    [few] vojske se oporavljaju na jedan potez.
    *[other] vojski se oporavljaju na jedan potez.
}
ageofheroes-eruption-strikes-you = { $attacker } igra erupciju protiv vas. Jedan vaš grad je uništen.
ageofheroes-eruption-strikes = { $attacker } igra erupciju protiv igrača { $player }.
ageofheroes-city-destroyed = Erupcija uništava grad.

# Fair phase
ageofheroes-fair-start = U marketu počinje novi dan.
ageofheroes-fair-draw-base = Vučete { $count } { $count ->
    [one] kartu
    [few] karte
    *[other] karata
}.
ageofheroes-fair-draw-roads = Vučete još { $count }  { $count ->
    [one] kartu
    [few] karte
    *[other] karata
} zahvaljujući vašoj mreži puteva.
ageofheroes-fair-draw-other = { $player } vuče { $count } { $count ->
    [one] kartu
    [few] karte
    *[other] karata
}.

# Trading/Auction
ageofheroes-auction-start = Razmena počinje.
ageofheroes-offer-trade = Ponudi razmenu
ageofheroes-offer-made = { $player } nudi { $card } za { $wanted }.
ageofheroes-offer-made-you = Nudite { $card } za { $wanted }.
ageofheroes-trade-accepted = { $player } prihvata ponudu igrača { $other } i menja { $give } za { $receive }.
ageofheroes-trade-accepted-you = Prihvatate ponudu igrača { $other } i dobijate { $receive }.
ageofheroes-trade-cancelled = { $player } povlači svoju ponudu za kartu { $card }.
ageofheroes-trade-cancelled-you = Povlačite vašu ponudu za kartu { $card }.
ageofheroes-stop-trading = Zaustavi razmenu
ageofheroes-select-request = Nudite { $card }. Šta želite za nju?
ageofheroes-cancel = Otkaži
ageofheroes-left-auction = { $player } napušta razmenu.
ageofheroes-left-auction-you = Napuštate razmenu.
ageofheroes-any-card = Bilo koju kartu
ageofheroes-cannot-trade-own-special = Ne možete da razmenite vaš poseban resurs.
ageofheroes-resource-not-in-game = Ovaj poseban resurs se ne koristi u ovoj igri.

# Main play phase
ageofheroes-play-start = Faza igranja.
ageofheroes-day = Dan { $day }
ageofheroes-draw-card = { $player } vuče kartu iz špila.
ageofheroes-draw-card-you = Vučete { $card } iz špila.
ageofheroes-your-action = Šta želite da uradite?

# Tax Collection
ageofheroes-tax-collection = { $player } prikuplja poreze: { $cities } { $cities ->
    [one] grad
    [few] grada
    *[other] gradova
} uzima { $cards } { $cards ->
    [one] kartu
    [few] karte
    *[other] karata
}.
ageofheroes-tax-collection-you = Prikupljate poreze: { $cities } { $cities ->
    [one] grad
    [few] grada
    *[other] gradova
} uzimate { $cards } { $cards ->
    [one] kartu
    [few] karte
    *[other] karata
}.
ageofheroes-tax-no-city = Prikupljanje poreza: Nemate preživelih gradova. Odbacite kartu kako biste izvukli novu.
ageofheroes-tax-no-city-done = { $player } prikuplja poreze ali nema gradove, razmenjuje kartu.
ageofheroes-tax-no-city-done-you = Prikupljanje poreza: Zamenili ste { $card } za novu kartu.

# Construction
ageofheroes-construction-menu = Šta želite da gradite?
ageofheroes-construction-done = { $player } gradi { $article } { $building }.
ageofheroes-construction-done-you = Gradite { $article } { $building }.
ageofheroes-construction-stop = Zaustavi izgradnju
ageofheroes-construction-stopped = Odlučili ste da zaustavite izgradnju.
ageofheroes-road-select-neighbor = Izaberite sa kojim susedom želite da gradite put.
ageofheroes-direction-left = Sa leve strane
ageofheroes-direction-right = Sa desne strane
ageofheroes-road-request-sent = Zahtev za put poslat. Čekanje na potvrdu suseda.
ageofheroes-road-request-received = { $requester } zahteva dozvolu za izgradnju puta do vašeg plemena.
ageofheroes-road-request-denied-you = Odbili ste zahtev za put.
ageofheroes-road-request-denied = { $denier } odbija vaš zahtev za put.
ageofheroes-road-built = { $tribe1 } i { $tribe2 } su sada povezani putem.
ageofheroes-road-no-target = Nema dostupnih susednih plemena za izgradnju puta.
ageofheroes-approve = Dozvoli
ageofheroes-deny = Odbij
ageofheroes-supply-exhausted = Nema više { $building } dostupnih za izgradnju.

# Do Nothing
ageofheroes-do-nothing = { $player } preskače.
ageofheroes-do-nothing-you = Preskačete...

# War
ageofheroes-war-declare = { $attacker } objavljuje rat igraču { $defender }. Cilj: { $goal }.
ageofheroes-war-prepare = Izaberite vaše vojske za { $action }.
ageofheroes-war-no-army = Nemate dostupnih vojski ili karata heroja.
ageofheroes-war-no-targets = Nema dostupnih protivnika za rat.
ageofheroes-war-no-valid-goal = Nema ispravnih ciljeva za rat sa ovim protivnikom.
ageofheroes-war-select-target = Izaberite kog igrača želite da napadnete.
ageofheroes-war-select-goal = Izaberite vaš cilj rata.
ageofheroes-war-prepare-attack = Izaberite vaše trupe.
ageofheroes-war-prepare-defense = { $attacker } vas napada; izaberite vaše trupe.
ageofheroes-war-select-armies = Izaberite vojske: { $count }
ageofheroes-war-select-generals = Izaberite generale: { $count }
ageofheroes-war-select-heroes = Izaberite heroje: { $count }
ageofheroes-war-attack = Napad...
ageofheroes-war-defend = Odbrana...
ageofheroes-war-prepared = Vaše trupe: { $armies } { $armies ->
    [one] vojska
    [few] vojske
    *[other] vojski
}{ $generals ->
    [0] {""}
    [one] {" i 1 general"}
    *[other] {" i { $generals } generala"}
}{ $heroes ->
    [0] {""}
    [one] {" i 1 heroj"}
    *[other] {" i { $heroes } heroja"}
}.
ageofheroes-war-roll-you = Dobili ste { $roll }.
ageofheroes-war-roll-other = { $player } dobija { $roll }.
ageofheroes-war-bonuses-you = { $general ->
    [0] {
        { $fortress ->
            [0] {""}
            [1] {"+1 za tvrđavu = { $total } ukupno"}
                        *[other] {"+{ $fortress } za tvrđave = { $total } ukupno"}
        }
    }
    *[other] {
        { $fortress ->
            [0] {"+{ $general } za generala = { $total } ukupno"}
            [1] {"+{ $general } za generala, +1 za tvrđavu = { $total } ukupno"}
            *[other] {"+{ $general } za generala, +{ $fortress } za tvrđave = { $total } ukupno"}
        }
    }
}
ageofheroes-war-bonuses-other = { $general ->
    [0] {
        { $fortress ->
            [0] {""}
            [1] {"{ $player }: +1 za tvrđavu = { $total } ukupno"}
            *[other] {"{ $player }: +{ $fortress } za tvrđave = { $total } ukupno"}
        }
    }
    *[other] {
        { $fortress ->
            [0] {"{ $player }: +{ $general } za generala = { $total } ukupno"}
            [1] {"{ $player }: +{ $general } za generala, +1 za tvrđavu = { $total } ukupno"}
            *[other] {"{ $player }: +{ $general } za generala, +{ $fortress } za tvrđave = { $total } ukupno"}
        }
    }
}

# Battle
ageofheroes-battle-start = Borba počinje. { $att_armies } { $att_armies ->
    [one] vojska igrača { $attacker }
    [few] vojske igrača { $attacker }
    *[other] vojski igrača { $attacker }
} protiv { $def_armies } { $def_armies ->
    [one] vojske igrača { $defender }
    [few] vojske igrača { $defender }
    *[other] vojski igrača { $defender }
}.
ageofheroes-dice-roll-detailed = { $name } dobija { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } za generala" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 za tvrđavu" }
    *[other] { " + { $fortress } za tvrđave" }
} = { $total }.
ageofheroes-dice-roll-detailed-you = Dobili ste { $dice }{ $general ->
    [0] {""}
    *[other] { " + { $general } za generala" }
}{ $fortress ->
    [0] {""}
    [one] { " + 1 za tvrđavu" }
    *[other] { " + { $fortress } za tvrđave" }
} = { $total }.
ageofheroes-round-attacker-wins = { $attacker } pobeđuje ({ $att_total } protiv { $def_total }). { $defender } gubi vojsku.
ageofheroes-round-defender-wins = { $defender } se uspešno brani ({ $def_total } protiv { $att_total }). { $attacker } gubi vojsku.
ageofheroes-round-draw = Obe strane su izjednačene sa { $total }. Niko nije izgubio vojsku.
ageofheroes-battle-victory-attacker = { $attacker } pobeđuje igrača { $defender }.
ageofheroes-battle-victory-defender = { $defender } se uspešno brani od igrača { $attacker }.
ageofheroes-battle-mutual-defeat = I { $attacker } i { $defender } gube sve vojske.
ageofheroes-general-bonus = +{ $count } za { $count ->
    [one] generala
    *[other] generala
}
ageofheroes-fortress-bonus = +{ $count } za odbranu tvrđavom
ageofheroes-battle-winner = { $winner } pobeđuje u borbi.
ageofheroes-battle-draw = Borba se završava nerešeno...
ageofheroes-battle-continue = Nastavite borbu.
ageofheroes-battle-end = Borba je gotova.

# War outcomes
ageofheroes-conquest-success = { $attacker } osvaja { $count } { $count ->
    [one] grad
    [few] grada
    *[other] gradova
} igrača { $defender }.
ageofheroes-plunder-success = { $attacker } pljačka { $count } { $count ->
    [one] kartu
    [few] karte
    *[other] karata
} igrača { $defender }.
ageofheroes-destruction-success = { $attacker } uništava { $count } spomenika igrača { $defender }  { $count ->
    [one] resurs
    *[other] resursa
}.
ageofheroes-army-losses = { $player } gubi { $count } { $count ->
    [one] vojsku
    [few] vojske
    *[other] vojski
}.
ageofheroes-army-losses-you = Gubite { $count } { $count ->
    [one] vojsku
    [few] vojske
    *[other] vojski
}.

# Army return
ageofheroes-army-return-road = Vaše vojske se odmah vraćaju putem.
ageofheroes-army-return-delayed = { $count } { $count ->
    [one] jedinica se vraća
    [few] jedinice se vraćaju
    *[other] jedinica se vraća
} na kraju vašeg sledećeg poteza.
ageofheroes-army-returned = Trupe igrača { $player } su se vratile iz rata.
ageofheroes-army-returned-you = Vaše trupe su se vratile iz rata.
ageofheroes-army-recover = Vojske igrača { $player } se oporavljaju od zemljotresa.
ageofheroes-army-recover-you = Vaše vojske se oporavljaju od zemljotresa.

# Olympics
ageofheroes-olympics-cancel = { $player } igra Olimpijske igre. Rat otkazan.
ageofheroes-olympics-prompt = { $attacker } proglašava rat. Imate Olimpijske igre - da li želite da ih iskoristite da otkažete rat?
ageofheroes-yes = Da
ageofheroes-no = Ne

# Monument progress
ageofheroes-monument-progress = Popunjenost spomenika igrača { $player }  { $count }/5.
ageofheroes-monument-progress-you = Popunjenost vašeg spomenika { $count }/5.

# Hand management
ageofheroes-discard-excess = Imate više od { $max } karata. Odbacite { $count } { $count ->
    [one] kartu
    [few] karte
    *[other] karata
}.
ageofheroes-discard-excess-other = { $player } mora da odbaci dodatne karte.
ageofheroes-discard-more = Odbacite još { $count }  { $count ->
    [one] kartu
    [few] karte
    *[other] karata
}.

# Victory
ageofheroes-victory-cities = { $player } ima pet gradova! Carstvo pet gradova.
ageofheroes-victory-cities-you = Imate pet gradova! Carstvo pet gradova.
ageofheroes-victory-monument = { $player } ima potpun spomenik! Nosioci su značajne kulture.
ageofheroes-victory-monument-you = Popunili ste vaš spomenik! Nosioci ste značajne kulture.
ageofheroes-victory-last-standing = { $player } je poslednje preostalo pleme! Najuporniji.
ageofheroes-victory-last-standing-you = Vi ste poslednje preostalo pleme! Najuporniji.
ageofheroes-game-over = Igra je gotova.

# Elimination
ageofheroes-eliminated = { $player } ispada.
ageofheroes-eliminated-you = Ispali ste.

# Hand
ageofheroes-hand-empty = Nemate karata.
ageofheroes-hand-contents = Vaša ruka ({ $count } { $count ->
    [one] karta
    [few] karte
    *[other] karata
}): { $cards }

# Status
ageofheroes-status = { $player } ({ $tribe }): { $cities } { $cities ->
    [one] grad
    [few] grada
    *[other] gradova
}, { $armies } { $armies ->
    [one] vojska
    [few] vojske
    *[other] vojski
}, { $monument }/5 spomenik
ageofheroes-status-detailed-header = { $player } ({ $tribe })
ageofheroes-status-cities = Gradovi: { $count }
ageofheroes-status-armies = Vojske: { $count }
ageofheroes-status-generals = Generali: { $count }
ageofheroes-status-fortresses = Tvrđave: { $count }
ageofheroes-status-monument = Spomenik: { $count }/5
ageofheroes-status-roads = Putevi: { $left }{ $right }
ageofheroes-status-road-left = levo
ageofheroes-status-road-right = desno
ageofheroes-status-none = Nema
ageofheroes-status-earthquake-armies = Vojske koje se oporavljaju: { $count }
ageofheroes-status-returning-armies = vojske koje se vraćaju: { $count }
ageofheroes-status-returning-generals = Generali koji se vraćaju: { $count }

# Deck info
ageofheroes-deck-empty = Nema više karata { $card } u špilu.
ageofheroes-deck-count = Preostalo karata: { $count }
ageofheroes-deck-reshuffled = Odbačene karte su promešane nazad u špil.

# Give up
ageofheroes-give-up-confirm = Da li ste sigurni da želite da se predate?
ageofheroes-gave-up = { $player } se predaje!
ageofheroes-gave-up-you = Predali ste se!

# Hero card
ageofheroes-hero-use = Koristite kao vojsku ili generala?
ageofheroes-hero-army = Vojska
ageofheroes-hero-general = General

# Fortune card
ageofheroes-fortune-reroll = { $player } koristi sreću za ponovno bacanje.
ageofheroes-fortune-prompt = Izgubili ste bacanje. Koristiti sreću za ponovno bacanje?

# Disabled action reasons
ageofheroes-not-your-turn = Niste na potezu.
ageofheroes-game-not-started = Igra još nije počela.
ageofheroes-wrong-phase = Ova radnja nije dostupna u trenutnoj fazi.
ageofheroes-no-resources = Nemate neophodne resurse.

# Building costs (for display)
ageofheroes-cost-army = 2 zrna, gvožđe
ageofheroes-cost-fortress = Gvožđe, drvo, kamen
ageofheroes-cost-general = Gvožđe, zlato
ageofheroes-cost-road = 2 kamena
ageofheroes-cost-city = 2 drveta, kamen
