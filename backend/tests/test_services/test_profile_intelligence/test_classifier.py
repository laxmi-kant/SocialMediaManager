"""Tests for LeadStatusClassifier."""

from unittest.mock import MagicMock, patch

from app.services.profile_intelligence.classifier import LeadStatusClassifier


def _make_lead(**kwargs):
    lead = MagicMock()
    lead.name = kwargs.get("name", "Jane Doe")
    lead.headline = kwargs.get("headline", "Software Engineer")
    lead.current_company = kwargs.get("company", "Acme Corp")
    lead.industry = kwargs.get("industry", "Technology")
    lead.location = kwargs.get("location", "San Francisco")
    return lead


class TestLeadStatusClassifier:
    def test_open_to_work(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="OPEN_TO_WORK")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead(headline="Open to new opportunities | Software Engineer")
        result = classifier.classify(lead)

        assert result == "OPEN_TO_WORK"
        mock_client.generate.assert_called_once()

    def test_hiring(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="HIRING")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead(headline="We're hiring! Head of Engineering")
        result = classifier.classify(lead)

        assert result == "HIRING"

    def test_business(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="BUSINESS")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead(headline="CEO & Founder at StartupXYZ")
        result = classifier.classify(lead)

        assert result == "BUSINESS"

    def test_general_fallback(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="GENERAL")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead(headline="Engineer at BigCo")
        result = classifier.classify(lead)

        assert result == "GENERAL"

    def test_invalid_response_defaults_to_general(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="unknown gibberish")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead()
        result = classifier.classify(lead)

        assert result == "GENERAL"

    def test_error_defaults_to_general(self):
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API down")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead()
        result = classifier.classify(lead)

        assert result == "GENERAL"

    def test_classify_uses_max_tokens_10(self):
        mock_client = MagicMock()
        mock_client.generate.return_value = MagicMock(text="HIRING")
        classifier = LeadStatusClassifier(ai_client=mock_client)

        lead = _make_lead()
        classifier.classify(lead)

        _, kwargs = mock_client.generate.call_args
        assert kwargs["max_tokens"] == 10
