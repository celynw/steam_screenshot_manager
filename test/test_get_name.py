from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import yaml
from steamfront.errors import AppNotFound

import steam_screenshot_manager.main as main_mod

if TYPE_CHECKING:
	from pathlib import Path

	import pytest

from steam_screenshot_manager.main import get_name


def setup_config_dir(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> Path:
	config_dir = tmp_path / ".config"
	monkeypatch.setattr(
		main_mod,
		"user_config_path",
		lambda *args, **kwargs: config_dir,
	)
	return config_dir


def write_replacements(config_dir: Path, content: dict[str, str]) -> None:
	config_dir.mkdir(parents=True, exist_ok=True)
	with (config_dir / "replacements.yml").open("w", encoding="utf-8") as f:
		yaml.dump(content, f)


def test_get_name_from_replacements(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	write_replacements(config_dir, {"233250": "Planetary Annihilation"})
	client = MagicMock()

	assert get_name(client, "233250") == "Planetary Annihilation"
	client.getApp.assert_not_called()


def test_get_name_from_steam(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	write_replacements(config_dir, {})
	client = MagicMock()
	client.getApp.return_value.name = "Half-Life"

	assert get_name(client, "70") == "Half-Life"


def test_get_name_app_not_found(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	write_replacements(config_dir, {})
	client = MagicMock()
	client.getApp.side_effect = AppNotFound("70")

	assert get_name(client, "70") is None


def test_get_name_type_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	write_replacements(config_dir, {})
	client = MagicMock()
	client.getApp.side_effect = TypeError

	assert get_name(client, "70") is None


def test_get_name_other_exception(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	write_replacements(config_dir, {})
	client = MagicMock()
	client.getApp.side_effect = RuntimeError

	assert get_name(client, "70") is None


def test_get_name_creates_default_replacements(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config_dir = setup_config_dir(tmp_path, monkeypatch)
	client = MagicMock()

	assert get_name(client, "233250") == "Planetary Annihilation"
	assert (config_dir / "replacements.yml").exists()
	client.getApp.assert_not_called()
