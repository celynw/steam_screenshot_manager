#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import steamfront
from natsort import natsorted
from tqdm import tqdm

from kellog import info, error, debug

# ==================================================================================================
def main(args):
	client = steamfront.Client()

	fileList = natsorted(args.dir.glob("*.png"))
	info(f"Found {len(fileList)} screenshots to sort")

	gameList = []
	for file in fileList:
		gameID = file.name.split("_")[0]
		if gameID not in gameList:
			gameList.append(gameID)
	info(f"Identified {len(gameList)} different games")

	badChars = '<>:"/\|?*'
	for i, gameID in enumerate(gameList):
		try:
			game = client.getApp(appid=gameID)
		except TypeError as e:
			error(e)
			error(f"Attempted gameID was `{gameID}`")
			continue
		except steamfront.app._AppNotFound as e:
			error(e)
			error(f"Attempted gameID was `{gameID}`")
			continue
		except:
			error("Some other error")
			error(f"Attempted gameID was `{gameID}`")
			continue

		name = game.name
		for char in badChars:
			name = name.replace(char, "_")
		info(f"{i + 1}/{len(gameList)}: {game.name}")

		# Make directory, move files over while renaming
		(args.dir / name).mkdir(exist_ok=True)
		for file in natsorted(args.dir.glob(f"{gameID}_*.png")):
			n = file.name.split(f"{gameID}_")[1]
			n = f"{n[:4]}-{n[4:6]}-{n[6:8]}_{n[8:10]}-{n[10:12]}-{n[12:]}"
			file.replace((args.dir / name / n).with_suffix(file.suffix))


# ==================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("--dir", "-d", type=str, metavar="PATH", default=Path.home() / "Pictures" / "Screenshots" / "Steam", help="Directory where the screenshots are stored")

	args = parser.parse_args()
	args.dir = Path(args.dir)

	return args


# ==================================================================================================
if __name__ == "__main__":
	main(parse_args())
