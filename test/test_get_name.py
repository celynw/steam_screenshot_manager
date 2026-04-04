from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from steamfront.errors import AppNotFound

from steam_screenshot_manager.main import get_name


def write_replacements(directory: Path, content: dict) -> None:
	with (directory / "replacements.yml").open("w") as f:
		yaml.dump(content, f)


def test_get_name_from_replacements(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.chdir(tmp_path)
	write_replacements(tmp_path, {"233250": "Planetary Annihilation"})
	client = MagicMock()
	assert get_name(client, "233250") == "Planetary Annihilation"
	client.getApp.assert_not_called()


def test_get_name_from_steam(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.chdir(tmp_path)
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.return_value.name = "Half-Life"
	assert get_name(client, "70") == "Half-Life"


def test_get_name_app_not_found(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.chdir(tmp_path)
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = AppNotFound("70")
	assert get_name(client, "70") is None


def test_get_name_type_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.chdir(tmp_path)
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = TypeError
	assert get_name(client, "70") is None


def test_get_name_other_exception(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.chdir(tmp_path)
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = RuntimeError
	assert get_name(client, "70") is None
