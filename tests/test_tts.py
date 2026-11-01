"""Tests for ElevenLabs TTS adapter."""

from voice_assistant.tts import ElevenLabsTTS


def test_stream_delegates_to_elevenlabs(monkeypatch) -> None:
    tts = ElevenLabsTTS("key", "voice", "model")
    captured: dict[str, object] = {}

    def fake_stream(**kwargs):
        captured.update(kwargs)
        yield b"pcm"

    monkeypatch.setattr(tts.client.text_to_speech, "convert_as_stream", fake_stream)

    assert list(tts.stream("Olá")) == [b"pcm"]
    assert captured["output_format"] == "pcm_44100"
    assert captured["voice_id"] == "voice"
