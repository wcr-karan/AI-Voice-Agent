"""
Tests for the webhook endpoint.
"""

import json
from unittest.mock import patch


class TestWebhookEndpoint:
    """Test POST /webhook."""

    def test_health_check(self, client):
        """Health endpoint returns 200."""
        test_client, _ = client
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Root endpoint returns welcome message."""
        test_client, _ = client
        response = test_client.get("/")
        assert response.status_code == 200
        assert "Welcome" in response.json()["message"]

    @patch("app.api.webhook.sheets_service")
    def test_call_started_event(self, mock_sheets, client, sample_webhook_call_ended):
        """call_started event returns success."""
        test_client, mocks = client
        payload = {
            "event": "call_started",
            "call": sample_webhook_call_ended["call"],
        }
        mocks["webhook"].return_value = json.dumps(payload).encode()

        response = test_client.post("/webhook")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch("app.api.webhook.sheets_service")
    def test_call_ended_event(self, mock_sheets, client, sample_webhook_call_ended):
        """call_ended event logs the call and returns success."""
        test_client, mocks = client
        mock_sheets.log_call.return_value = True
        mocks["webhook"].return_value = json.dumps(sample_webhook_call_ended).encode()

        response = test_client.post("/webhook")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_sheets.log_call.assert_called_once()

    @patch("app.api.webhook.sheets_service")
    def test_call_analyzed_event(self, mock_sheets, client, sample_webhook_call_analyzed):
        """call_analyzed event updates call log with analysis."""
        test_client, mocks = client
        mock_sheets.update_call_log.return_value = True
        mocks["webhook"].return_value = json.dumps(sample_webhook_call_analyzed).encode()

        response = test_client.post("/webhook")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_sheets.update_call_log.assert_called_once()

    @patch("app.api.webhook.sheets_service")
    def test_unknown_event_type(self, mock_sheets, client):
        """Unknown event type still returns success (graceful handling)."""
        test_client, mocks = client
        payload = {
            "event": "some_future_event",
            "call": {"call_id": "test_unknown"},
        }
        mocks["webhook"].return_value = json.dumps(payload).encode()

        response = test_client.post("/webhook")
        assert response.status_code == 200
