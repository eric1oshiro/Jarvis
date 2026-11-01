"""Tests for environment configuration."""

import pytest

from voice_assistant.config import ConfigError, Settings


def test_validate_rejects_placeholder_keys() -> None:
    settings = Settings(elevenlabs_api_key="cole_chave", anthropic_api_key="")

    with pytest.raises(ConfigError, match="ELEVENLABS_API_KEY"):
        settings.validate()


def test_validate_accepts_complete_settings() -> None:
    settings = Settings(elevenlabs_api_key="eleven-key", anthropic_api_key="anthropic-key")

    settings.validate()
