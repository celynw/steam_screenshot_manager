from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import yaml
from steamfront.errors import AppNotFound

import steam_screenshot_manager.main as main_mod

if TYPE_CHECKING:
	from pathlib import Path

	import pytest

from steam_screenshot_manager.main import get_name


def write_replacements(directory: Path, content: dict[str, str]) -> None:
	parent = directory.parent if directory.name else directory
	with (parent / "replacements.yml").open("w") as f:
		yaml.dump(content, f)


def test_get_name_from_replacements(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	write_replacements(tmp_path, {"233250": "Planetary Annihilation"})
	client = MagicMock()

	monkeypatch.setattr(main_mod, "__file__", str(tmp_path / "dummy.py"))
	assert get_name(client, "233250") == "Planetary Annihilation"
	client.getApp.assert_not_called()


def test_get_name_from_steam(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.return_value.name = "Half-Life"

	monkeypatch.setattr(main_mod, "__file__", str(tmp_path / "dummy.py"))
	assert get_name(client, "70") == "Half-Life"


def test_get_name_app_not_found(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = AppNotFound("70")

	monkeypatch.setattr(main_mod, "__file__", str(tmp_path / "dummy.py"))
	assert get_name(client, "70") is None


def test_get_name_type_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = TypeError

	monkeypatch.setattr(main_mod, "__file__", str(tmp_path / "dummy.py"))
	assert get_name(client, "70") is None


def test_get_name_other_exception(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	write_replacements(tmp_path, {})
	client = MagicMock()
	client.getApp.side_effect = RuntimeError

	monkeypatch.setattr(main_mod, "__file__", str(tmp_path / "dummy.py"))
	assert get_name(client, "70") is None
