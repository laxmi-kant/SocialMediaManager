"""AI-powered comment classification (sentiment + type)."""

import structlog

from app.models.comment import Comment
from app.services.ai_generator.client import AnthropicClientWrapper

logger = structlog.get_logger()

CLASSIFY_PROMPT = """Classify this social media comment. Return ONLY two words separated by a comma:
1. Sentiment: positive, negative, neutral, question
2. Type: praise, question, complaint, suggestion, spam, other

Comment: {comment_text}

Response format: sentiment,type"""


class CommentClassifier:
    """Classifies comments using Claude AI."""

    def __init__(self, ai_client: AnthropicClientWrapper | None = None):
        self.ai_client = ai_client or AnthropicClientWrapper()

    def classify(self, comment: Comment) -> tuple[str, str]:
        """Returns (sentiment, comment_type) tuple."""
        try:
            result = self.ai_client.generate(
                prompt=CLASSIFY_PROMPT.format(comment_text=comment.comment_text[:500]),
                max_tokens=20,
            )
            parts = result.text.strip().lower().split(",")
            sentiment = parts[0].strip() if len(parts) > 0 else "neutral"
            comment_type = parts[1].strip() if len(parts) > 1 else "other"

            valid_sentiments = {"positive", "negative", "neutral", "question"}
            valid_types = {"praise", "question", "complaint", "suggestion", "spam", "other"}

            sentiment = sentiment if sentiment in valid_sentiments else "neutral"
            comment_type = comment_type if comment_type in valid_types else "other"

            return sentiment, comment_type
        except Exception as exc:
            logger.warning("comment_classify_error", error=str(exc))
            return "neutral", "other"
