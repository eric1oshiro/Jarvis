"""Tests for provider-isolated conversation memory."""

from types import SimpleNamespace

from voice_assistant.llm import ClaudeConversation


def test_reply_sends_history_and_saves_turn(monkeypatch) -> None:
    conversation = ClaudeConversation("key", "model", "system", 4)
    captured: dict[str, object] = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(text="Olá!")])

    monkeypatch.setattr(conversation.client.messages, "create", fake_create)

    assert conversation.reply("Oi") == "Olá!"
    assert captured["messages"] == [{"role": "user", "content": "Oi"}]
    assert list(conversation.history) == [
        {"role": "user", "content": "Oi"},
        {"role": "assistant", "content": "Olá!"},
    ]
