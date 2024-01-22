#!/usr/bin/env python3
import argparse
from pathlib import Path

import steamfront
from kellog import error, info
from natsort import natsorted
from steamfront.errors import AppNotFound


# ======================================================================================================================
def main(args) -> None:
	client = steamfront.Client()

	paths = natsorted(args.dir.glob("*.png"))
	info(f"Found {len(paths)} screenshots to sort")

	game_list = []
	for path in paths:
		game_id = path.stem.split("_")[0]
		if game_id not in game_list:
			game_list.append(game_id)
	info(f"Identified {len(game_list)} different games")

	bad_chars = r'<>:"/\|?*'
	for i, game_id in enumerate(game_list):
		try:
			game = client.getApp(appid=game_id)
		except TypeError as e:
			error(e)
			error(f"Attempted gameID was `{game_id}`")
			continue
		except AppNotFound as e:
			error(e)
			error(f"Attempted gameID was `{game_id}`")
			continue
		except:
			error("Some other error")
			error(f"Attempted gameID was `{game_id}`")
			continue

		name = str(game.name)
		info(f"{i + 1}/{len(game_list)}: {name}")
		for char in bad_chars:
			name = name.replace(char, "_")

		# Make directory, move files over while renaming
		(args.dir / name).mkdir(exist_ok=True)
		for path in natsorted(args.dir.glob(f"{game_id}_*.png")):
			n = path.name.split(f"{game_id}_")[1]
			n = f"{n[:4]}-{n[4:6]}-{n[6:8]}_{n[8:10]}-{n[10:12]}-{n[12:]}"
			dest = (args.dir / name / n).with_suffix(path.suffix)
			if not dest.exists():
				path.replace(dest)
			else:
				error(f"Destination '{dest.relative_to(args.dir)}' exists when moving '{path.relative_to(args.dir)}'")


# ======================================================================================================================
def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument(
		"--dir",
		"-d",
		type=str,
		metavar="PATH",
		default=Path.home() / "Pictures" / "Screenshots" / "Steam",
		help="Directory where the screenshots are stored",
	)

	args = parser.parse_args()
	args.dir = Path(args.dir)

	return args


# ======================================================================================================================
if __name__ == "__main__":
	main(parse_args())
