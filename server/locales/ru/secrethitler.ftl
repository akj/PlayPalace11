# Secret Hitler — English locale

game-name-secrethitler = Secret Hitler
category-social-deduction = Social deduction

# Options menu
sh-set-vote-timeout = President vote timeout: { $seconds } seconds
sh-enter-vote-timeout = Enter president vote timeout in seconds (30 to 600)
sh-option-changed-vote-timeout = President vote timeout is now { $seconds } seconds.
sh-desc-vote-timeout = How long the president has to call the vote before it auto-calls.
sh-set-bot-think = Bot think time: { $seconds } seconds
sh-enter-bot-think = Enter bot think time in seconds (0 to 10)
sh-option-changed-bot-think = Bot think time is now { $seconds } seconds.
sh-desc-bot-think = Delay bots wait before acting, in seconds.

# Prestart errors
sh-error-need-5-players = Secret Hitler requires 5 to 10 players.

# Role reveal (private)
sh-you-are-liberal = You are a Liberal.
sh-you-are-fascist = You are a Fascist.
sh-you-are-hitler = You are Hitler.
sh-fascist-teammates = The Fascists are: { $names }. Hitler is: { $hitler }.
sh-hitler-knows-teammates = The Fascists are: { $names }. You are Hitler.
sh-acknowledge-role = Acknowledge role

# Nomination
sh-president-is = { $player } is President.
sh-you-are-president = You are President.
sh-president-nominates = { $president } nominates { $chancellor } as Chancellor.
sh-president-can-call-vote = Discussion is open. When ready, call for the vote.
sh-nominate = Nominate { $player }
sh-call-vote = Call for vote
sh-cancel-nomination = Cancel nomination
sh-vote-timeout-approaching = Vote will auto-call in { $seconds } seconds.

# Voting
sh-voting-open = Voting is open. Ja or Nein?
sh-vote-ja = Ja!
sh-vote-nein = Nein!
sh-you-voted-ja = You voted Ja!
sh-you-voted-nein = You voted Nein!
sh-players-still-voting = Still voting: { $names }.
sh-vote-result =
    { $passed ->
        [true] The vote passes.
       *[false] The vote fails.
    }
sh-vote-roll-call = { $player } voted { $vote ->
        [ja] Ja!
       *[nein] Nein!
    }.

# Legislation
sh-president-draws = President draws three policies.
sh-your-policies = Your policies: { $p1 }, { $p2 }, { $p3 }.
sh-president-discards = President discards one policy.
sh-chancellor-receives = Chancellor receives two policies.
sh-your-policies-chancellor = Your policies: { $p1 }, { $p2 }.
sh-discard-policy = Discard: { $policy }
sh-enact-policy = Enact: { $policy }
sh-propose-veto = Propose veto
sh-chancellor-enacts =
    { $policy ->
        [liberal] A Liberal policy is enacted. Liberal track: { $liberal } of 5.
       *[fascist] A Fascist policy is enacted. Fascist track: { $fascist } of 6.
    }
sh-policy-liberal = Liberal
sh-policy-fascist = Fascist

# Election tracker / chaos
sh-tracker-advances = Election tracker is at { $count } of 3.
sh-chaos-top-policy = Chaos! The top policy is enacted automatically.

# Executive powers
sh-power-investigate = President will investigate a player's loyalty.
sh-investigate-target = Investigate { $player }
sh-you-see-party =
    { $party ->
        [liberal] { $player } is a Liberal.
       *[fascist] { $player } is a Fascist.
    }
sh-power-special-election = President will call a special election.
sh-choose-president-target = Choose { $player } as next President
sh-power-policy-peek = President peeks at the top three policies.
sh-you-peek = Top three policies: { $p1 }, { $p2 }, { $p3 }.
sh-acknowledge-peek = Acknowledge
sh-power-execution = President will execute a player.
sh-execute-target = Execute { $player }
sh-player-executed = { $player } has been executed.

# Veto
sh-chancellor-proposes-veto = Chancellor proposes to veto this agenda.
sh-veto-accept = Accept veto
sh-veto-reject = Reject veto
sh-president-accepts-veto = President accepts the veto. Both policies are discarded.
sh-president-rejects-veto = President rejects the veto. Chancellor must enact.

# Persistent (standard) actions
sh-view-tracks = View policy tracks
sh-view-tracks-content = Liberal track: { $liberal } of 5. Fascist track: { $fascist } of 6.
sh-view-government = View government
sh-view-government-content = President: { $president }. Chancellor: { $chancellor }. Previous elected: { $lastpres } / { $lastchan }.
sh-view-players = View players
sh-view-my-role = View my role
sh-view-election-tracker = View election tracker

# Win conditions
sh-liberals-win-policies = Liberals win! Five Liberal policies enacted.
sh-liberals-win-execution = Liberals win! Hitler has been executed.
sh-fascists-win-policies = Fascists win! Six Fascist policies enacted.
sh-fascists-win-hitler-elected = Fascists win! Hitler was elected Chancellor after three Fascist policies.
sh-final-roles = Final roles: { $lines }
sh-final-role-line = { $player } — { $role ->
        [liberal] Liberal
        [fascist] Fascist
       *[hitler] Hitler
    }

# Disconnect / pause
sh-paused-for-reconnect = Game paused — waiting for { $player } to reconnect.
sh-resumed = Game resumed.
sh-forfeit = Forfeit disconnected player
