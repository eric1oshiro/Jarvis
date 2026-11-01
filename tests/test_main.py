"""Tests for small CLI helpers."""

import pytest

from voice_assistant.main import is_exit_command


@pytest.mark.parametrize("text", ["tchau", "Pode encerrar agora", "TCHAU, assistente"])
def test_exit_commands(text: str) -> None:
    assert is_exit_command(text)


def test_regular_text_is_not_exit_command() -> None:
    assert not is_exit_command("qual é a previsão do tempo?")
