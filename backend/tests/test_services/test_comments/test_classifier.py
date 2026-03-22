"""Unit tests for CommentClassifier."""

from unittest.mock import MagicMock, patch

from app.models.comment import Comment
from app.services.ai_generator.client import GenerationResult
from app.services.comments.classifier import CommentClassifier


class TestCommentClassifier:
    def test_classify_positive_praise(self):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="positive,praise", model="test", input_tokens=10, output_tokens=5,
        )
        classifier = CommentClassifier(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.comment_text = "Great article! Very insightful."

        sentiment, ctype = classifier.classify(comment)
        assert sentiment == "positive"
        assert ctype == "praise"

    def test_classify_question(self):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="question,question", model="test", input_tokens=10, output_tokens=5,
        )
        classifier = CommentClassifier(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.comment_text = "How do I implement this?"

        sentiment, ctype = classifier.classify(comment)
        assert sentiment == "question"
        assert ctype == "question"

    def test_classify_invalid_response_defaults(self):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="garbage_output", model="test", input_tokens=10, output_tokens=5,
        )
        classifier = CommentClassifier(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.comment_text = "Some comment"

        sentiment, ctype = classifier.classify(comment)
        assert sentiment == "neutral"
        assert ctype == "other"

    def test_classify_error_returns_defaults(self):
        mock_ai = MagicMock()
        mock_ai.generate.side_effect = Exception("API error")
        classifier = CommentClassifier(ai_client=mock_ai)

        comment = MagicMock(spec=Comment)
        comment.comment_text = "Test"

        sentiment, ctype = classifier.classify(comment)
        assert sentiment == "neutral"
        assert ctype == "other"
