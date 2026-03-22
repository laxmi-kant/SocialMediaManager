"""Unit tests for LinkedInPublisher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.publishers.linkedin import LinkedInPublisher


@pytest.fixture
def publisher():
    return LinkedInPublisher()


@pytest.fixture
def mock_account():
    account = MagicMock()
    account.access_token = "encrypted_token"
    account.platform_user_id = "abc123"
    return account


class TestLinkedInPublisher:
    def test_platform_name(self, publisher):
        assert publisher.platform_name == "linkedin"

    def test_format_post_adds_hashtags(self, publisher):
        result = publisher._format_post("Great article about AI", ["#AI", "#Tech"])
        assert "#AI" in result
        assert "#Tech" in result

    def test_format_post_no_duplicate_tags(self, publisher):
        result = publisher._format_post("Great #AI article", ["#AI", "#ML"])
        assert result.count("#AI") == 1
        assert "#ML" in result

    @patch("app.services.publishers.linkedin.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.linkedin.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_publish_success(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {"x-restli-id": "urn:li:share:123456"}
        mock_response.json.return_value = {}
        mock_client.post.return_value = mock_response

        result = await publisher.publish("LinkedIn post", ["#AI"], mock_account)

        assert result.success is True
        assert result.platform_post_id == "urn:li:share:123456"
        assert "linkedin.com" in result.platform_url

    @patch("app.services.publishers.linkedin.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.linkedin.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_publish_failure(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.post.side_effect = Exception("401 Unauthorized")

        result = await publisher.publish("Test", [], mock_account)

        assert result.success is False
        assert "Unauthorized" in result.error_message

    @patch("app.services.publishers.linkedin.decrypt_token", return_value="real_token")
    @patch("app.services.publishers.linkedin.ResilientHTTPClient")
    @pytest.mark.asyncio
    async def test_get_metrics(self, mock_http_cls, mock_decrypt, publisher, mock_account):
        mock_client = AsyncMock()
        mock_http_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_http_cls.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "likesSummary": {"totalLikes": 30},
            "commentsSummary": {"totalFirstLevelComments": 5},
            "sharesSummary": {"totalShares": 3},
        }
        mock_client.get.return_value = mock_response

        metrics = await publisher.get_metrics("urn:li:share:123", mock_account)

        assert metrics.likes == 30
        assert metrics.comments == 5
        assert metrics.shares == 3
