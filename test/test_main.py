from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from typer.testing import CliRunner

from steam_screenshot_manager.main import app

runner = CliRunner()


def test_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.chdir(tmp_path)
	with (tmp_path / "replacements.yml").open("w") as f:
		yaml.dump({}, f)
	(tmp_path / "70_20240115091234_1.png").touch()
	(tmp_path / "70_20240122134553_1.png").touch()
	(tmp_path / "220_20240115091302_1.png").touch()

	games = {"70": "Half-Life", "220": "Half-Life 2"}

	def get_app(appid: str) -> MagicMock:
		mock = MagicMock()
		mock.name = games[appid]
		return mock

	mock_client = MagicMock()
	mock_client.getApp.side_effect = get_app

	with patch(
		"steam_screenshot_manager.main.steamfront.Client",
		return_value=mock_client,
	):
		result = runner.invoke(app, ["--dir", str(tmp_path)])

	assert result.exit_code == 0
	assert (tmp_path / "Half-Life" / "2024-01-15_09-12-34_1.png").exists()
	assert (tmp_path / "Half-Life" / "2024-01-22_13-45-53_1.png").exists()
	assert (tmp_path / "Half-Life 2" / "2024-01-15_09-13-02_1.png").exists()


def test_main_skips_unknown_game(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.chdir(tmp_path)
	with (tmp_path / "replacements.yml").open("w") as f:
		yaml.dump({}, f)
	(tmp_path / "99999_20240115091234_1.png").touch()

	mock_client = MagicMock()
	mock_client.getApp.side_effect = RuntimeError

	with patch(
		"steam_screenshot_manager.main.steamfront.Client",
		return_value=mock_client,
	):
		result = runner.invoke(app, ["--dir", str(tmp_path)])

	assert result.exit_code == 0
	assert (tmp_path / "99999_20240115091234_1.png").exists()
