"""Microphone capture and PCM playback."""

from __future__ import annotations

import logging
from collections.abc import Iterable

import numpy as np
import sounddevice as sd


class AudioError(RuntimeError):
    """Raised when an audio device cannot be used."""


class NoSpeechDetected(AudioError):
    """Raised when recording ends without detected speech."""


class AudioRecorder:
    """Record until speech is followed by silence."""

    def __init__(
        self,
        sample_rate: int,
        channels: int,
        silence_threshold: float,
        silence_duration_seconds: float,
        max_recording_seconds: float,
        input_device: int | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration_seconds = silence_duration_seconds
        self.max_recording_seconds = max_recording_seconds
        self.input_device = input_device

    def record(self) -> np.ndarray:
        """Capture mono float audio after detecting a non-silent block."""
        blocksize = max(256, self.sample_rate // 10)
        blocks: list[np.ndarray] = []
        heard_speech = False
        silent_frames = 0
        total_frames = 0
        max_frames = int(self.max_recording_seconds * self.sample_rate)
        silence_frames_needed = int(self.silence_duration_seconds * self.sample_rate)

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocksize=blocksize,
                device=self.input_device,
            ) as stream:
                while total_frames < max_frames:
                    data, _overflowed = stream.read(blocksize)
                    total_frames += len(data)
                    level = float(np.sqrt(np.mean(np.square(data))))
                    is_silent = level < self.silence_threshold
                    if not heard_speech and is_silent:
                        continue
                    heard_speech = True
                    blocks.append(data.copy())
                    silent_frames = silent_frames + len(data) if is_silent else 0
                    if silent_frames >= silence_frames_needed:
                        break
        except sd.PortAudioError as error:
            raise AudioError(
                "Não foi possível acessar o microfone. Verifique permissões, conexão e INPUT_DEVICE."
            ) from error

        if not blocks:
            raise NoSpeechDetected("Nenhuma fala detectada. Tente falar mais alto ou ajuste SILENCE_THRESHOLD.")
        if total_frames >= max_frames:
            logging.warning("Tempo máximo de gravação atingido; enviando áudio capturado.")
        return np.concatenate(blocks, axis=0)


class PCMPlayer:
    """Play a stream of signed 16-bit little-endian PCM chunks."""

    def __init__(self, sample_rate: int = 44100, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels

    def play(self, chunks: Iterable[bytes]) -> None:
        """Play chunks as they arrive, reducing TTS latency."""
        remainder = b""
        try:
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
            ) as stream:
                for chunk in chunks:
                    raw = remainder + bytes(chunk)
                    usable = len(raw) - (len(raw) % 2)
                    remainder = raw[usable:]
                    if usable:
                        samples = np.frombuffer(raw[:usable], dtype="<i2").astype(np.float32) / 32768.0
                        stream.write(samples.reshape(-1, self.channels))
        except sd.PortAudioError as error:
            raise AudioError("Não foi possível reproduzir o áudio. Verifique o alto-falante.") from error
