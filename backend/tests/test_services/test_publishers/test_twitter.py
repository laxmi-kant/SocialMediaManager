"""Unit tests for TwitterPublisher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.publishers.twitter import TwitterPublisher


@pytest.fixture
def publisher():
    return TwitterPublisher()


@pytest.fixture
def mock_account():
    account = MagicMock()
    account.access_token = "encrypted_token"
    account.display_name = "@testuser"
    return account


class TestTwitterPublisher:
    def test_platform_name(self, publisher):
        assert publisher.platform_name == "twitter"

    def test_format_tweet_short(self, publisher):
        result = publisher._format_tweet("Hello world", ["#AI", "#Tech"])
        assert "#AI" in result
        assert "#Tech" in result
        assert len(result) <= 280

    def test_format_tweet_skips_existing_hashtags(self, publisher):
        result = publisher._format_tweet("Hello #AI world", ["#AI", "#Tech"])
        # Should not duplicate #AI
        assert result.count("#AI") == 1
        assert "#Tech" in result

    def test_format_tweet_truncates_long(self, publisher):
        long_text = "A" * 278
        result = publisher._format_tweet(long_text, ["#Tag"])
        assert len(result) <= 280
        # Hashtag should not be added since text is too long
        assert "#Tag" not in result

    @patch("app.services.publishers.twitter.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.twitter.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_publish_success(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"id": "12345"}}
        mock_client.post.return_value = mock_response

        result = await publisher.publish("Test tweet", ["#AI"], mock_account)

        assert result.success is True
        assert result.platform_post_id == "12345"
        assert "12345" in result.platform_url

    @patch("app.services.publishers.twitter.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.twitter.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_publish_failure(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.post.side_effect = Exception("API rate limited")

        result = await publisher.publish("Test tweet", [], mock_account)

        assert result.success is False
        assert "rate limited" in result.error_message

    @patch("app.services.publishers.twitter.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.twitter.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_get_metrics(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "public_metrics": {
                    "impression_count": 1000,
                    "like_count": 50,
                    "reply_count": 10,
                    "retweet_count": 5,
                    "quote_count": 2,
                }
            }
        }
        mock_client.get.return_value = mock_response

        metrics = await publisher.get_metrics("12345", mock_account)

        assert metrics.impressions == 1000
        assert metrics.likes == 50
        assert metrics.comments == 10
        assert metrics.shares == 7  # retweets + quotes
