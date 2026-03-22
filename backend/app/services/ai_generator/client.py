"""Anthropic Claude API client wrapper."""

from dataclasses import dataclass

import anthropic
import structlog

from app.config import settings

logger = structlog.get_logger()


@dataclass
class GenerationResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class AnthropicClientWrapper:
    """Wrapper around the Anthropic SDK with token tracking."""

    def __init__(self, default_model: str | None = None):
        self.default_model = default_model or settings.default_ai_model
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> GenerationResult:
        model = model or self.default_model
        messages = [{"role": "user", "content": prompt}]

        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)

        text = response.content[0].text if response.content else ""
        usage = response.usage

        logger.info(
            "ai_generation",
            model=model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )

        return GenerationResult(
            text=text,
            model=model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )
