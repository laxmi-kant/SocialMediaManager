"""Unit tests for Anthropic client wrapper."""

from unittest.mock import MagicMock, patch

from app.services.ai_generator.client import AnthropicClientWrapper, GenerationResult


class TestAnthropicClientWrapper:
    @patch("app.services.ai_generator.client.anthropic.Anthropic")
    @patch("app.services.ai_generator.client.settings")
    def test_generate_returns_result(self, mock_settings, mock_anthropic_cls):
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.default_ai_model = "claude-haiku-4-5-20251001"

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated tweet about AI #AI #Tech")]
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 30
        mock_client.messages.create.return_value = mock_response

        wrapper = AnthropicClientWrapper(default_model="claude-haiku-4-5-20251001")
        result = wrapper.generate(prompt="Write a tweet", system="You are helpful")

        assert isinstance(result, GenerationResult)
        assert result.text == "Generated tweet about AI #AI #Tech"
        assert result.model == "claude-haiku-4-5-20251001"
        assert result.input_tokens == 50
        assert result.output_tokens == 30

        mock_client.messages.create.assert_called_once_with(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Write a tweet"}],
            system="You are helpful",
        )

    @patch("app.services.ai_generator.client.anthropic.Anthropic")
    @patch("app.services.ai_generator.client.settings")
    def test_generate_without_system_prompt(self, mock_settings, mock_anthropic_cls):
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.default_ai_model = "claude-haiku-4-5-20251001"

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        mock_client.messages.create.return_value = mock_response

        wrapper = AnthropicClientWrapper()
        wrapper.generate(prompt="Hi")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert "system" not in call_kwargs

    @patch("app.services.ai_generator.client.anthropic.Anthropic")
    @patch("app.services.ai_generator.client.settings")
    def test_generate_custom_model_and_tokens(self, mock_settings, mock_anthropic_cls):
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.default_ai_model = "claude-haiku-4-5-20251001"

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 200
        mock_client.messages.create.return_value = mock_response

        wrapper = AnthropicClientWrapper()
        result = wrapper.generate(prompt="Prompt", model="claude-sonnet-4-6", max_tokens=2048)

        assert result.model == "claude-sonnet-4-6"
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"
        assert call_kwargs["max_tokens"] == 2048

    @patch("app.services.ai_generator.client.anthropic.Anthropic")
    @patch("app.services.ai_generator.client.settings")
    def test_generate_empty_content(self, mock_settings, mock_anthropic_cls):
        mock_settings.anthropic_api_key = "test-key"
        mock_settings.default_ai_model = "claude-haiku-4-5-20251001"

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = []
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 0
        mock_client.messages.create.return_value = mock_response

        wrapper = AnthropicClientWrapper()
        result = wrapper.generate(prompt="Bad prompt")

        assert result.text == ""
