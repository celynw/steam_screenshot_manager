# Steam Screenshot Manager

Turns this:

```text
70_20240115091234_1.png
70_20240122134553_1.png
220_20240115091302_1.png
730_20240201183045_1.png
730_20240201183112_1.png
730_20240201183140_1.png
```

Into this:

```text
Half-Life/
├── 2024-01-15_09-12-34_1.png
└── 2024-01-22_13-45-53_1.png
Half-Life 2/
└── 2024-01-15_09-13-02_1.png
Counter-Strike 2/
├── 2024-02-01_18-30-45_1.png
├── 2024-02-01_18-31-12_1.png
└── 2024-02-01_18-31-40_1.png
```

Renames and organises Steam's uncompressed screenshots into per-game subdirectories.

## Installation

Requires [`uv`](https://docs.astral.sh/uv/).

```bash
uv tool install /path/to/steam_screenshot_manager
```

Then optionally enable tab completion:

```bash
steam_screenshot_manager --install-completion
```

## Usage

```bash
steam_screenshot_manager -d /path/to/screenshots
```

## Unrecognised games

Some games may not be found in the Steam database — typically delisted games or non-Steam games added to your library.

You can add overrides to `replacements.yml` in the user config directory.
On Linux this is usually `~/.config/steam_screenshot_manager/replacements.yml`.

The file is created automatically on first run with the bundled defaults.
The key is the Steam game ID (the first component of the original filename).
