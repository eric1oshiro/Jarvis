"""Provider-isolated LLM conversation layer."""

from __future__ import annotations

from collections import deque
from typing import Any

from anthropic import Anthropic


class LLMError(RuntimeError):
    """Raised when the language model cannot produce a response."""


class ClaudeConversation:
    """Short-term conversational memory backed by Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, system_prompt: str, max_history_messages: int) -> None:
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.history: deque[dict[str, str]] = deque(maxlen=max_history_messages)

    def reply(self, user_text: str) -> str:
        """Generate an assistant reply and save the completed turn."""
        messages: list[dict[str, str]] = [*self.history, {"role": "user", "content": user_text}]
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=250,
                system=self.system_prompt,
                messages=messages,
            )
            text = self._text_from_response(response).strip()
        except Exception as error:
            raise LLMError("Não foi possível gerar uma resposta. Verifique chave Anthropic, conexão e limites da API.") from error
        if not text:
            raise LLMError("O modelo retornou uma resposta vazia.")
        self.history.extend(({"role": "user", "content": user_text}, {"role": "assistant", "content": text}))
        return text

    @staticmethod
    def _text_from_response(response: Any) -> str:
        """Extract text blocks, tolerating future non-text response blocks."""
        return "".join(getattr(block, "text", "") for block in response.content)
