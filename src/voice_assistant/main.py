"""Command-line entry point for the voice assistant."""

from __future__ import annotations

import argparse
import logging
import re
import sys
import unicodedata

from .audio import AudioError, AudioRecorder, NoSpeechDetected, PCMPlayer
from .config import ConfigError, Settings
from .llm import ClaudeConversation, LLMError
from .stt import ElevenLabsSTT, TranscriptionError
from .tts import ElevenLabsTTS, SynthesisError


def is_exit_command(text: str) -> bool:
    """Return true when a Portuguese voice exit word appears in the transcript."""
    normalized = unicodedata.normalize("NFD", text.lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return bool(re.search(r"\b(tchau|encerrar)\b", normalized))


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(description="Assistente virtual por voz")
    parser.add_argument("--debug", action="store_true", help="Exibe logs detalhados")
    return parser


def run(settings: Settings) -> None:
    """Run the conversation loop until the user says goodbye or interrupts it."""
    settings.validate()
    recorder = AudioRecorder(
        sample_rate=settings.sample_rate,
        channels=settings.channels,
        silence_threshold=settings.silence_threshold,
        silence_duration_seconds=settings.silence_duration_seconds,
        max_recording_seconds=settings.max_recording_seconds,
        input_device=settings.input_device,
    )
    stt = ElevenLabsSTT(settings.elevenlabs_api_key, settings.stt_model, settings.language_code, settings.sample_rate)
    llm = ClaudeConversation(settings.anthropic_api_key, settings.anthropic_model, settings.system_prompt, settings.max_history_messages)
    tts = ElevenLabsTTS(settings.elevenlabs_api_key, settings.voice_id, settings.tts_model)
    player = PCMPlayer()

    print("Assistente pronto. Fale após 'Ouvindo…'. Diga 'tchau' ou 'encerrar' para sair.")
    while True:
        try:
            print("\nOuvindo…")
            audio = recorder.record()
            transcript = stt.transcribe(audio)
            if not transcript:
                print("Não entendi. Pode repetir?")
                continue
            print(f"Você: {transcript}")
            if is_exit_command(transcript):
                print("Assistente: Até logo!")
                player.play(tts.stream("Até logo!"))
                return
            answer = llm.reply(transcript)
            print(f"Assistente: {answer}")
            player.play(tts.stream(answer))
        except NoSpeechDetected as error:
            print(str(error))
        except (AudioError, TranscriptionError, LLMError, SynthesisError) as error:
            logging.error("%s", error)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.exception("Detalhes do erro")
        except KeyboardInterrupt:
            print("\nEncerrando. Até logo!")
            return


def main() -> None:
    """Parse arguments and start the assistant."""
    args = build_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run(Settings.from_env())
    except ConfigError as error:
        print(f"Configuração inválida: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
