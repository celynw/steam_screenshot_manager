"""steam-screenshot-manager."""

from importlib import resources
from pathlib import Path
from typing import Annotated

import steamfront
import typer
import yaml
from kellog import error, info
from natsort import natsorted
from platformdirs import user_config_path
from steamfront.errors import AppNotFound

app = typer.Typer()
APP_NAME = "steam_screenshot_manager"
REPLACEMENTS_FILE = "replacements.yml"


@app.command()
def main(
	directory: Annotated[
		Path,
		typer.Option(
			...,
			"--dir",
			"-d",
			help="Directory where the screenshots are stored",
		),
	],
) -> None:
	"""Run steam-screenshot-manager."""
	paths = natsorted(directory.glob("*.png"))
	info(f"Found {len(paths)} screenshots to sort")

	game_list = []
	for path in paths:
		game_id = path.stem.split("_")[0]
		if game_id not in game_list:
			game_list.append(game_id)
	info(f"Identified {len(game_list)} different games")

	client = steamfront.Client()
	for i, game_id in enumerate(game_list):
		name = get_name(client, game_id)
		if name is None:
			continue
		info(f"{i + 1}/{len(game_list)}: {name}")
		move_screenshots(game_id, name, directory)


def get_name(client: steamfront.Client, game_id: str) -> str | None:
	"""
	Retrieve the name of a game given the game ID.

	Parameters
	----------
	client
		Steamfront client
	game_id
		Steam game ID, taken from the screenshot filename

	Returns
	-------
		Sanitised game name, or None if the game ID is invalid
	"""
	# Check if the game ID is in the replacements file
	replacements = load_replacements()
	if game_id in replacements:
		return sanitise_name(replacements[game_id])

	# If not, query the steam database
	try:
		game = client.getApp(appid=game_id)
		return sanitise_name(str(game.name))
	except TypeError as e:
		error(e)
		error(f"Attempted gameID was `{game_id}`")
		return None
	except AppNotFound as e:
		error(e)
		error(f"Attempted gameID was `{game_id}`")
		return None
	except Exception as e:  # noqa: BLE001
		error(e)
		error(f"Attempted gameID was `{game_id}`")
		return None


def get_replacements_path() -> Path:
	"""
	Return the user replacements file, creating it from bundled defaults.

	Returns
	-------
		Path to the user replacements file
	"""
	config_dir = Path(user_config_path(APP_NAME, ensure_exists=True))
	config_dir.mkdir(parents=True, exist_ok=True)
	replacements_path = config_dir / REPLACEMENTS_FILE
	if not replacements_path.exists():
		default_replacements = resources.files(APP_NAME).joinpath(REPLACEMENTS_FILE)
		replacements_path.write_text(
			default_replacements.read_text(encoding="utf-8"),
			encoding="utf-8",
		)
	return replacements_path


def load_replacements() -> dict[str, str]:
	"""
	Load replacements from the user config directory.

	Returns
	-------
		Configured game ID replacements
	"""
	with get_replacements_path().open(encoding="utf-8") as replacements_file:
		replacements = yaml.safe_load(replacements_file) or {}
	if isinstance(replacements, dict):
		return {str(game_id): str(name) for game_id, name in replacements.items()}

	error("Invalid replacements config, expected a mapping")
	return {}


def sanitise_name(name: str) -> str:
	"""
	Remove/replace characters that are not allowed in filenames.

	Parameters
	----------
	name
		Game name to sanitise

	Returns
	-------
		Sanitised game name
	"""
	bad_chars = r'<>:"/\|?*'
	name = str(name)
	for char in bad_chars:
		name = name.replace(char, "_")

	return name


def move_screenshots(game_id: str, name: str, directory: Path) -> None:
	"""
	Move screenshots to a new directory, renaming them in the process.

	Parameters
	----------
	game_id
		Steam game ID, taken from the screenshot file
	name
		Sanitised game name
	directory
		Screenshot directory
	"""
	# Make directory, move files over while renaming
	(directory / name).mkdir(exist_ok=True)
	for path in natsorted(directory.glob(f"{game_id}_*.png")):
		n = path.name.split(f"{game_id}_")[1]
		n = f"{n[:4]}-{n[4:6]}-{n[6:8]}_{n[8:10]}-{n[10:12]}-{n[12:]}"
		dest = (directory / name / n).with_suffix(path.suffix)
		if not dest.exists():
			path.replace(dest)
		else:
			error(
				f"Destination '{dest.relative_to(directory)}' exists when moving "
				f"'{path.relative_to(directory)}'",
			)


if __name__ == "__main__":
	app()
