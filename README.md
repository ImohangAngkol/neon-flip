# Neon Flip

Neon Flip is a small, single-file arcade game built with Python and Tkinter. Dodge hazards, collect gems, build a combo, and survive as the pace gradually increases.

## Features

- Two-lane movement with smooth lane changes
- Neon-styled hazards, gems, particles, and score popups
- Three lives, temporary damage protection, and forgiving collision bounds
- Gem combos and Overdrive, which lets you smash hazards for bonus points
- Pause and resume, plus persistent local high scores
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
| Space or click | Start, then flip to the other lane |
| A / D or Left / Right | Choose the left or right lane |
| P or Escape | Pause or resume |
| Click while paused | Resume |
| R | Start a fresh run |
| Enter | Start from the menu |

## How to Play

Stay out of the lane occupied by each red hazard and collect gold gems for points. Collecting gems in a row builds a combo multiplier; the combo fades after a short break. Seven gems charge Overdrive for five seconds. During Overdrive, the player is protected and can smash hazards for bonus points.

A quick lane change near a hazard can earn a close-call bonus. You have three lives. After taking damage, brief invulnerability prevents repeated hits while the damage effect is visible. The score rises as you survive, and obstacle speed increases over time.

Your best score is stored in `neon_flip_highscore.json` beside the game file. It is created when a new record is reached and can be deleted to reset the record. The game continues to work if the file is absent, invalid, or the folder cannot be written.
