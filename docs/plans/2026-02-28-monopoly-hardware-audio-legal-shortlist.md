# Monopoly Hardware Audio Legal Shortlist (Strict Pass)

Date: 2026-02-28  
Branch: `monopoly`

## Scope

Target event IDs:

- `play_theme`
- `star_wars_theme`
- `junior_coin_sound_powerup`
- `mario_question_block_sound`

This pass focuses on "closest-to-board feel" while keeping redistributable licensing clear.

## Legal Status Key

- `ship_now_attribution`: Can be committed and redistributed now with attribution kept in-repo.
- `ship_now_sharealike_review`: Usable, but verify project-level compatibility if we distribute derivatives/remixes.
- `reference_only`: Useful for matching tone, but do not ship as bundled assets without explicit rights.

## Ranked Candidates

### `junior_coin_sound_powerup`

1. `8-Bit Sound Library/Mp3/Collect_Point_00.mp3` (currently installed, transcoded to OGG)
   - Source pack: OpenGameArt 8-Bit Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: short retro pickup; closest to Mario-style coin cadence among tested legal packs
   - Sample duration: ~0.68s (source MP3)
   - Status: `ship_now_attribution`
2. `8-Bit Sound Library/Mp3/Pickup_01.mp3`
   - Source pack: OpenGameArt 8-Bit Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: very short pickup; stronger "blip" feel, weaker "coin reward" feel
   - Sample duration: ~0.31s
   - Status: `ship_now_attribution`
3. `bfxr_sounds.zip` coin effect (8-bit platformer SFX page)
   - Source: OpenGameArt 8-bit platformer SFX
   - License: CC-BY 3.0
   - Fit notes: deliberately retro coin style; good fallback if we want alternate timbre
   - Status: `ship_now_attribution`
4. `Coins Sound Library/Mp3/Coins_Single/Coins_Single_12.mp3`
   - Source pack: OpenGameArt Coins Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: realistic metal coin, less Mario-like
   - Sample duration: ~0.26s
   - Status: `ship_now_attribution`
5. Question Block unit recordings from actual Super Mario Monopoly boards/videos
   - Fit notes: best authenticity
   - Licensing note: Nintendo/Hasbro owned IP and branded SFX references
   - Status: `reference_only`

### `mario_question_block_sound`

1. `8-Bit Sound Library/Mp3/Collect_Point_00.mp3` (currently installed, transcoded to OGG)
   - Source pack: OpenGameArt 8-Bit Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: short pickup cue that matches Question Block "coin ping" behavior in the Celebration manual
   - Sample duration: ~0.68s (source MP3)
   - Status: `ship_now_attribution`
2. `8-Bit Sound Library/Mp3/Pickup_01.mp3`
   - Source pack: OpenGameArt 8-Bit Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: alternate shorter cue for lower playback latency
   - Sample duration: ~0.31s
   - Status: `ship_now_attribution`
3. `Coins Sound Library/Mp3/Coins_Single/Coins_Single_12.mp3`
   - Source pack: OpenGameArt Coins Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: realistic metallic coin variant
   - Sample duration: ~0.26s
   - Status: `ship_now_attribution`
4. Direct recordings from Monopoly Super Mario Celebration Question Block unit
   - Fit notes: highest authenticity
   - Licensing note: Nintendo/Hasbro owned IP and branded SFX references
   - Status: `reference_only`

### `star_wars_theme`

1. `Sci-Fi Sound Library/Mp3/Jingle_Win_01.mp3` (currently installed, transcoded to OGG)
   - Source pack: OpenGameArt Sci-Fi Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: space/jingle tone, closer to sci-fi board identity than orchestral fanfare
   - Sample duration: ~6.01s
   - Status: `ship_now_attribution`
2. `Electric Sound Library/Mp3/Jingle_Win_Synth/Jingle_Win_Synth_03.mp3`
   - Source pack: OpenGameArt Electric Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: short synth win cue; good if we want lower latency on repeated triggers
   - Sample duration: ~1.80s
   - Status: `ship_now_attribution`
3. `WIN_AGAINST_CHAMPION_0.ogg`
   - Source: OpenGameArt Fanfares
   - License options on page: CC-BY 4.0 / CC-BY 3.0 / CC-BY-SA 4.0 / CC-BY-SA 3.0
   - Fit notes: strong cue but more "victory brass" than "space motif"
   - Status: `ship_now_sharealike_review`
4. `spacetheme.ogg`
   - Source: OpenGameArt Space Theme
   - License: CC-BY 3.0
   - Fit notes: music bed option; may be too long/heavy for frequent event trigger
   - Status: `ship_now_attribution`
5. Star Wars official score clips / direct board-recorded licensed franchise music
   - Fit notes: highest authenticity
   - Licensing note: Star Wars products are licensed by Lucasfilm; franchise music rights are not included by default for redistribution in this repo
   - Status: `reference_only`

### `play_theme`

1. `Electric Sound Library/Mp3/SpaceEngine/SpaceEngine_Start_01.mp3` (currently installed, transcoded to OGG)
   - Source pack: OpenGameArt Electric Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: startup identity cue; better match for "board boots/starts" style event
   - Sample duration: ~2.04s
   - Status: `ship_now_attribution`
2. `Sci-Fi Sound Library/Mp3/Menu_Select_01.mp3` (or `_00`)
   - Source pack: OpenGameArt Sci-Fi Sound Effects Library
   - License: CC-BY 3.0
   - Fit notes: very short event ping, suitable for frequent triggers
   - Status: `ship_now_attribution`
3. `TITLE BOUT_0.ogg`
   - Source: OpenGameArt Fanfares
   - License options on page: CC-BY 4.0 / CC-BY 3.0 / CC-BY-SA 4.0 / CC-BY-SA 3.0
   - Fit notes: recognizable but long and brass-forward
   - Status: `ship_now_sharealike_review`
4. Kenney RPG SFX single click/metal cue
   - Source: OpenGameArt 50 RPG Sound Effects (CC0)
   - Fit notes: very short and safe fallback; lower thematic fit
   - Status: `ship_now_attribution`
5. Direct recordings of Hasbro proprietary board startup sounds
   - Fit notes: highest authenticity
   - Licensing note: Hasbro product content is protected by IP rights on official instruction pages
   - Status: `reference_only`

## Recommendation

Recommended legal swap set (closest fit + lowest license friction):

1. Keep `junior_coin_sound_powerup` as current `Collect_Point_00` mapping.
2. Use `star_wars_theme` from Sci-Fi pack `Jingle_Win_01`.
3. Use `play_theme` from Electric pack `SpaceEngine_Start_01`.
4. Use `mario_question_block_sound` from 8-bit pack `Collect_Point_00`.

Status on this branch: applied.  
All four live mappings now resolve to CC-BY 3.0 stand-ins from the same author/publisher family (Little Robot Sound Factory), which simplifies attribution and keeps a coherent synthesis style.

## Sources

- Nintendo Game Content Guidelines (official):  
  https://www.nintendo.co.jp/networkservice_guideline/en/index.html?n
- Hasbro Monopoly Super Mario Celebration instructions/product info:  
  https://instructions.hasbro.com/en-us/instruction/monopoly-super-mario-celebration-edition-board-game-instructions
- Hasbro Monopoly Star Wars Mandalorian instructions/product info:  
  https://instructions.hasbro.com/en-us/instruction/monopoly-star-wars-the-mandalorian-edition-board-game
- OpenGameArt 8-Bit Sound Effects Library (CC-BY 3.0):  
  https://opengameart.org/content/8-bit-sound-effects-library
- OpenGameArt 8-bit platformer SFX (CC-BY 3.0):  
  https://opengameart.org/content/8-bit-platformer-sfx
- OpenGameArt Sci-Fi Sound Effects Library (CC-BY 3.0):  
  https://opengameart.org/content/sci-fi-sound-effects-library
- OpenGameArt Electric Sound Effects Library (CC-BY 3.0):  
  https://opengameart.org/content/electric-sound-effects-library
- OpenGameArt Coins Sound Effects Library (CC-BY 3.0):  
  https://opengameart.org/content/coins-sound-effects-library
- OpenGameArt Fanfares (multi-license options):  
  https://opengameart.org/content/fanfares
- OpenGameArt Space Theme (CC-BY 3.0):  
  https://opengameart.org/content/space-theme

## Notes

- This document is an engineering shortlist, not legal advice.
- "reference_only" ratings above are based on source terms and IP ownership statements; treat as conservative compliance guidance for repository redistribution.
