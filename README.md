# Neon Flip 1.2

Neon Flip is a small, single-file arcade game built with Python and Tkinter. Pick a mode, dodge hazards, collect gems, build combos, and survive as the pace gradually increases.

## Features

- Two-lane movement with smooth lane changes
- Neon-styled hazards, gems, particles, and score popups
- Classic mode: three lives and a balanced difficulty curve
- Rush mode: one life, faster hazards, and 1.5x scoring
- Rare shield pickups absorb one collision; shields do not stack
- Gem combos and Overdrive, which lets you smash hazards for bonus points
- Separate saved high scores for Classic and Rush
- Optional, non-blocking Windows system sounds
- Pause and resume, forgiving collision bounds, and clean restarts
- No third-party packages

## Requirements

- Python 3.8 or newer
- Tkinter, included with most standard Python installations

On Windows, the standard installer from python.org includes Tcl/Tk. To check Tkinter, run `python -m tkinter`; a small test window should appear.

## Run

Open PowerShell or Command Prompt in the project folder and run:

```powershell
python neon_flip.py
```

If `python` is not recognized, try `py neon_flip.py`.

## Controls

| Input | Action |
| --- | --- |
| Left / Right or 1 / 2 (menu) | Select Classic or Rush |
| Enter, Space, or click (menu) | Start the selected mode |
| Space or click (during a run) | Flip to the other lane |
| A / D or Left / Right (during a run) | Choose the left or right lane |
| P or Escape (during a run) | Pause or resume |
| Click while paused | Resume |
| R | Restart the current mode |
| Escape (results screen) | Return to mode selection |
| M | Toggle sound effects |

## How to Play

Stay out of the lane occupied by each red hazard and collect gold gems for points. Blue shield pickups appear occasionally in the safe lane. A shield protects against one hazard collision, then breaks; it does not use a life. Shields cannot stack. Overdrive destroys hazards without consuming an active shield.

Collecting gems in a row builds a combo multiplier; the combo fades after a short break. Seven gems charge Overdrive for five seconds. During Overdrive, the player is protected and can smash hazards for bonus points. A quick lane change near a hazard can earn a close-call bonus.

Classic starts with three lives. Rush starts with one life, has a faster but capped obstacle pace, and awards 1.5 times the score. Each wave has one hazard. Its same-wave gem or shield, when present, appears in the other, safe lane. Optional bonus gems can appear later. After damage, brief invulnerability prevents repeated hits.

## High Scores and Sound

Mode records are stored in `neon_flip_highscore.json` beside the game file. Existing Version 1.1 `high_score` data is kept as the Classic record when the new format is loaded. The file is updated when a new record is earned. Missing, malformed, or incomplete data is handled safely. Sound effects use asynchronous Windows system sounds when available; on unsupported systems, sound starts disabled and gameplay remains unchanged.
