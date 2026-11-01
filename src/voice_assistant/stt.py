"""ElevenLabs Scribe integration."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from elevenlabs.client import ElevenLabs


class TranscriptionError(RuntimeError):
    """Raised when speech-to-text fails."""


class ElevenLabsSTT:
    """Transcribe local microphone audio with ElevenLabs Scribe."""

    def __init__(self, api_key: str, model_id: str, language_code: str, sample_rate: int) -> None:
        self.client = ElevenLabs(api_key=api_key)
        self.model_id = model_id
        self.language_code = language_code
        self.sample_rate = sample_rate

    def transcribe(self, audio: np.ndarray) -> str:
        """Write captured audio to a temporary WAV and return its transcript."""
        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
                path = Path(temp.name)
            sf.write(path, audio, self.sample_rate, subtype="PCM_16")
            with path.open("rb") as audio_file:
                result = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id=self.model_id,
                    language_code=self.language_code,
                )
            return str(result.text).strip()
        except Exception as error:
            raise TranscriptionError(
                "Falha na transcrição. Verifique sua conexão, chave ElevenLabs e limites da API."
            ) from error
        finally:
            if path:
                path.unlink(missing_ok=True)
