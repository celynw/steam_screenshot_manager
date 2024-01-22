# Steam Screenshot Manager

Steam's 'uncompressed' (actually means losslessly compressed) screenshots are not named for humans.
This script automatically renames and organises them into game subdirectories.

e.g.

| Original path             | Modified path                         |
| ------------------------- | ------------------------------------- |
| `70_20240122134553_1.png` | `Half-Life/2024-01-22_13-45-53_1.png` |

The components of the original path are:

- Game ID
- Year
- Month
- Day
- Hours
- Minutes
- Seconds
- Iteration (in rare case of duplicates)

Some games may not be detected.
Possible reasons are because the game is no longer listed, or it is a non-Steam game.
Overrides may be listed in the `replacements.yml` file, as :

```yml
GAME_ID: "Desired title"
```

## Running

Install requirements with:

```bash
pip install -r requirements.txt
```

then run as:

```none
./steam_screenshot_manager.py

usage: steam_screenshot_manager.py [-h] [--dir PATH]

options:
  -h, --help           show this help message and exit
  --dir PATH, -d PATH  Directory where the screenshots are stored (default: $HOME/Pictures/Screenshots/Steam)
```
