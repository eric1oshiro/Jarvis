"""ElevenLabs text-to-speech integration."""

from __future__ import annotations

from collections.abc import Iterator

from elevenlabs.client import ElevenLabs


class SynthesisError(RuntimeError):
    """Raised when voice synthesis fails."""


class ElevenLabsTTS:
    """Produce a streaming 44.1 kHz PCM response."""

    def __init__(self, api_key: str, voice_id: str, model_id: str) -> None:
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model_id = model_id

    def stream(self, text: str) -> Iterator[bytes]:
        """Yield PCM chunks from ElevenLabs as soon as they are available."""
        try:
            yield from self.client.text_to_speech.convert_as_stream(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                output_format="pcm_44100",
            )
        except Exception as error:
            raise SynthesisError(
                "Falha ao gerar a voz. Verifique chave ElevenLabs, VOICE_ID e limites da API."
            ) from error
