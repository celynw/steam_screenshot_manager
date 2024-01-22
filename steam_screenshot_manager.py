#!/usr/bin/env python3
import argparse
from pathlib import Path
import yaml

import steamfront
from kellog import error, info
from natsort import natsorted
from steamfront.errors import AppNotFound


def main(args: argparse.Namespace) -> None:
	paths = natsorted(args.dir.glob("*.png"))
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
		move_screenshots(game_id, name, args.dir)


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
	with (Path().cwd() / "replacements.yml").open() as f:
		replacements = yaml.safe_load(f)
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
	except:
		error("Some other error")
		error(f"Attempted gameID was `{game_id}`")
		return None


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


def move_screenshots(game_id: str, name: str, dir: Path) -> None:
	"""
	Move screenshots to a new directory, renaming them in the process.

	Parameters
	----------
	game_id
		Steam game ID, taken from the screenshot file
	name
		Sanitised game name
	dir
		Screenshot directory
	"""
	# Make directory, move files over while renaming
	(dir / name).mkdir(exist_ok=True)
	for path in natsorted(dir.glob(f"{game_id}_*.png")):
		n = path.name.split(f"{game_id}_")[1]
		n = f"{n[:4]}-{n[4:6]}-{n[6:8]}_{n[8:10]}-{n[10:12]}-{n[12:]}"
		dest = (dir / name / n).with_suffix(path.suffix)
		if not dest.exists():
			path.replace(dest)
		else:
			error(f"Destination '{dest.relative_to(dir)}' exists when moving '{path.relative_to(dir)}'")


def parse_args() -> argparse.Namespace:
	"""
	Parse command line arguments.

	Returns
	-------
		Arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument(
		"--dir",
		"-d",
		type=Path,
		metavar="PATH",
		default=Path.home() / "Pictures" / "Screenshots" / "Steam",
		help="Directory where the screenshots are stored",
	)

	return parser.parse_args()


if __name__ == "__main__":
	main(parse_args())
