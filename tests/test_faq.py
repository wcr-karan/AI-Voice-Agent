"""
Tests for the FAQ endpoint and FAQ service.
"""

import json
from unittest.mock import patch


class TestFAQEndpoint:
    """Test POST /check-faq."""

    @patch("app.api.faq.faq_service")
    def test_faq_found(self, mock_svc, client, sample_faq_payload):
        """Returns answer when FAQ match is found."""
        test_client, mocks = client
        mocks["faq"].return_value = json.dumps(sample_faq_payload).encode()

        from app.models.faq import FAQResponse
        mock_svc.lookup.return_value = FAQResponse(
            found=True,
            answer="Our teeth whitening starts at $299.",
            category="pricing",
            message="Our teeth whitening starts at $299.",
        )

        response = test_client.post("/check-faq")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["found"] is True
        assert "$299" in data["result"]["answer"]

    @patch("app.api.faq.faq_service")
    def test_faq_not_found(self, mock_svc, client, sample_faq_payload):
        """Returns not found when no FAQ match exists."""
        test_client, mocks = client
        sample_faq_payload["args"]["question"] = "Do you perform brain surgery?"
        mocks["faq"].return_value = json.dumps(sample_faq_payload).encode()

        from app.models.faq import FAQResponse
        mock_svc.lookup.return_value = FAQResponse(
            found=False,
            message="I don't have that specific information.",
        )

        response = test_client.post("/check-faq")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["found"] is False


class TestFAQService:
    """Test faq_service business logic."""

    def test_tokenize(self):
        """Tokenizes text correctly."""
        from app.services.faq_service import FAQService
        svc = FAQService()
        tokens = svc._tokenize("How much does teeth whitening cost?")
        assert "whitening" in tokens
        assert "cost" in tokens
        assert "how" in tokens

    def test_empty_question(self):
        """Returns not-found for empty questions."""
        from app.services.faq_service import FAQService
        svc = FAQService()
        svc._faq_cache = []  # Empty cache
        result = svc.lookup("")
        assert result.found is False

    @patch("app.services.faq_service.sheets_service")
    def test_keyword_matching(self, mock_sheets):
        """Matches FAQ by keyword overlap."""
        mock_sheets.get_all_faqs.return_value = [
            {
                "ID": 1,
                "Category": "pricing",
                "Question": "How much does teeth whitening cost?",
                "Answer": "Teeth whitening starts at $299.",
                "Keywords": "whitening, cost, price, how much",
            },
        ]

        from app.services.faq_service import FAQService
        svc = FAQService()
        result = svc.lookup("What is the cost of whitening?")
        assert result.found is True
        assert "$299" in result.answer

    @patch("app.services.faq_service.sheets_service")
    def test_no_match_below_threshold(self, mock_sheets):
        """Returns not-found when score is below threshold."""
        mock_sheets.get_all_faqs.return_value = [
            {
                "ID": 1,
                "Category": "pricing",
                "Question": "How much does teeth whitening cost?",
                "Answer": "Teeth whitening starts at $299.",
                "Keywords": "whitening, cost, price",
            },
        ]

        from app.services.faq_service import FAQService
        svc = FAQService()
        result = svc.lookup("something completely unrelated to dentistry")
        assert result.found is False
