from pathlib import Path

import pytest

from steam_screenshot_manager.main import move_screenshots, sanitise_name


def make_screenshots(directory: Path, *names: str) -> None:
	for name in names:
		(directory / name).touch()


def test_readme_examples(tmp_path: Path) -> None:
	make_screenshots(tmp_path, "70_20240115091234_1.png", "70_20240122134553_1.png")
	move_screenshots("70", "Half-Life", tmp_path)
	assert (tmp_path / "Half-Life" / "2024-01-15_09-12-34_1.png").exists()
	assert (tmp_path / "Half-Life" / "2024-01-22_13-45-53_1.png").exists()

	make_screenshots(tmp_path, "220_20240115091302_1.png")
	move_screenshots("220", "Half-Life 2", tmp_path)
	assert (tmp_path / "Half-Life 2" / "2024-01-15_09-13-02_1.png").exists()

	make_screenshots(
		tmp_path,
		"730_20240201183045_1.png",
		"730_20240201183112_1.png",
		"730_20240201183140_1.png",
	)
	move_screenshots("730", "Counter-Strike 2", tmp_path)
	assert (tmp_path / "Counter-Strike 2" / "2024-02-01_18-30-45_1.png").exists()
	assert (tmp_path / "Counter-Strike 2" / "2024-02-01_18-31-12_1.png").exists()
	assert (tmp_path / "Counter-Strike 2" / "2024-02-01_18-31-40_1.png").exists()


def test_originals_removed(tmp_path: Path) -> None:
	make_screenshots(tmp_path, "70_20240115091234_1.png")
	move_screenshots("70", "Half-Life", tmp_path)
	assert not (tmp_path / "70_20240115091234_1.png").exists()


def test_only_matching_game_moved(tmp_path: Path) -> None:
	make_screenshots(tmp_path, "70_20240115091234_1.png", "220_20240115091302_1.png")
	move_screenshots("70", "Half-Life", tmp_path)
	assert (tmp_path / "220_20240115091302_1.png").exists()


def test_duplicate_destination_left_in_place(tmp_path: Path) -> None:
	make_screenshots(tmp_path, "70_20240115091234_1.png")
	(tmp_path / "Half-Life").mkdir()
	(tmp_path / "Half-Life" / "2024-01-15_09-12-34_1.png").touch()
	move_screenshots("70", "Half-Life", tmp_path)
	assert (tmp_path / "70_20240115091234_1.png").exists()


@pytest.mark.parametrize(
	("name", "expected"),
	[
		("Half-Life 2", "Half-Life 2"),
		(
			'PLAYERUNKNOWN\'S BATTLEGROUNDS: "test"',
			"PLAYERUNKNOWN'S BATTLEGROUNDS_ _test_",
		),
		("C:/Game", "C__Game"),
		("Game<1>", "Game_1_"),
	],
)
def test_sanitise_name(name: str, expected: str) -> None:
	assert sanitise_name(name) == expected
