"""Environment-based configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(ValueError):
    """Raised when required configuration is absent or invalid."""


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    elevenlabs_api_key: str
    anthropic_api_key: str
    language_code: str = "pt"
    stt_model: str = "scribe_v2"
    tts_model: str = "eleven_multilingual_v2"
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    system_prompt: str = (
        "Você é um assistente de voz prestativo. Responda em português, de forma breve e natural."
    )
    max_history_messages: int = 12
    sample_rate: int = 16000
    channels: int = 1
    silence_threshold: float = 0.015
    silence_duration_seconds: float = 1.2
    max_recording_seconds: float = 20.0
    input_device: int | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from `.env` and the process environment."""
        load_dotenv()
        raw_device = os.getenv("INPUT_DEVICE", "").strip()
        try:
            return cls(
                elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "").strip(),
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
                language_code=os.getenv("LANGUAGE_CODE", "pt").strip(),
                stt_model=os.getenv("ELEVENLABS_STT_MODEL", "scribe_v2").strip(),
                tts_model=os.getenv("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2").strip(),
                voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip(),
                anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929").strip(),
                system_prompt=os.getenv("SYSTEM_PROMPT", cls.system_prompt),
                max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "12")),
                sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
                channels=int(os.getenv("CHANNELS", "1")),
                silence_threshold=float(os.getenv("SILENCE_THRESHOLD", "0.015")),
                silence_duration_seconds=float(os.getenv("SILENCE_DURATION_SECONDS", "1.2")),
                max_recording_seconds=float(os.getenv("MAX_RECORDING_SECONDS", "20")),
                input_device=int(raw_device) if raw_device else None,
            )
        except ValueError as error:
            raise ConfigError(f"Valor inválido no arquivo .env: {error}") from error

    def validate(self) -> None:
        """Validate settings needed to contact external APIs."""
        missing = [
            name
            for name, value in (
                ("ELEVENLABS_API_KEY", self.elevenlabs_api_key),
                ("ANTHROPIC_API_KEY", self.anthropic_api_key),
            )
            if not value or value.startswith("cole_")
        ]
        if missing:
            raise ConfigError(f"Configure {', '.join(missing)} no arquivo .env.")
        if self.max_history_messages < 2 or self.max_history_messages % 2:
            raise ConfigError("MAX_HISTORY_MESSAGES deve ser um número par maior ou igual a 2.")
        if self.sample_rate <= 0 or self.channels <= 0:
            raise ConfigError("SAMPLE_RATE e CHANNELS devem ser positivos.")
