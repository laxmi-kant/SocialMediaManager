"""Unit tests for CommentReplyGenerator."""

from unittest.mock import MagicMock

from app.models.comment import Comment, CommentReply
from app.services.ai_generator.client import GenerationResult
from app.services.comments.reply_generator import CommentReplyGenerator


class TestCommentReplyGenerator:
    def test_generate_reply(self):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="Thank you for your kind words! We appreciate the feedback.",
            model="claude-haiku-4-5-20251001",
            input_tokens=100,
            output_tokens=30,
        )
        generator = CommentReplyGenerator(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.id = "test-id"
        comment.commenter_name = "John"
        comment.comment_text = "Great post!"
        comment.sentiment = "positive"
        comment.comment_type = "praise"

        reply = generator.generate_reply(comment, post_text="AI is amazing")

        assert isinstance(reply, CommentReply)
        assert reply.reply_text == "Thank you for your kind words! We appreciate the feedback."
        assert reply.ai_suggested_text == reply.reply_text
        assert reply.reply_mode == "ai_suggested"
        assert reply.status == "draft"
        assert reply.token_usage == {"input_tokens": 100, "output_tokens": 30}

    def test_generate_reply_with_tone(self):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="Haha, glad you enjoyed it!",
            model="test",
            input_tokens=50,
            output_tokens=20,
        )
        generator = CommentReplyGenerator(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.id = "test-id"
        comment.commenter_name = "Jane"
        comment.comment_text = "LOL this is hilarious"
        comment.sentiment = "positive"
        comment.comment_type = "praise"

        reply = generator.generate_reply(comment, post_text="Funny joke", tone="casual")

        # Verify prompt included the tone
        call_args = mock_ai.generate.call_args
        assert "casual" in call_args[1]["prompt"]
