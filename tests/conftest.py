"""
Shared test fixtures and configuration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client with signature verification disabled."""
    with patch("app.api.webhook.verify_retell_signature") as mock_wh, \
         patch("app.api.booking.verify_retell_signature") as mock_bk, \
         patch("app.api.availability.verify_retell_signature") as mock_av, \
         patch("app.api.faq.verify_retell_signature") as mock_fq, \
         patch("app.api.transfer.verify_retell_signature") as mock_tr:

        # Each mock will be configured per test to return the right body
        mock_wh.return_value = b'{}'
        mock_bk.return_value = b'{}'
        mock_av.return_value = b'{}'
        mock_fq.return_value = b'{}'
        mock_tr.return_value = b'{}'

        yield TestClient(app), {
            "webhook": mock_wh,
            "booking": mock_bk,
            "availability": mock_av,
            "faq": mock_fq,
            "transfer": mock_tr,
        }


@pytest.fixture
def sample_booking_payload():
    """Sample booking request payload."""
    return {
        "args": {
            "customer_name": "John Smith",
            "customer_phone": "+1234567890",
            "customer_email": "john@example.com",
            "service_type": "Dental Cleaning",
            "appointment_date": "2027-07-05",
            "appointment_time": "10:00 AM",
        },
        "call_id": "call_test_123",
    }


@pytest.fixture
def sample_availability_payload():
    """Sample availability check payload."""
    return {
        "args": {
            "service_type": "Dental Cleaning",
            "preferred_date": "2027-07-05",
        },
        "call_id": "call_test_123",
    }


@pytest.fixture
def sample_webhook_call_ended():
    """Sample call_ended webhook payload."""
    return {
        "event": "call_ended",
        "call": {
            "call_id": "call_test_456",
            "call_type": "phone_call",
            "from_number": "+1234567890",
            "to_number": "+0987654321",
            "direction": "inbound",
            "start_timestamp": 1719900000000,
            "end_timestamp": 1719900300000,
            "retell_llm_dynamic_variables": {
                "customer_name": "John Smith",
                "booking_id": "BK-20270705-001",
            },
        },
    }


@pytest.fixture
def sample_webhook_call_analyzed():
    """Sample call_analyzed webhook payload."""
    return {
        "event": "call_analyzed",
        "call": {
            "call_id": "call_test_789",
            "call_type": "phone_call",
            "from_number": "+1234567890",
            "to_number": "+0987654321",
            "direction": "inbound",
            "call_analysis": {
                "call_summary": "Patient called to book a dental cleaning.",
                "user_sentiment": "positive",
            },
            "retell_llm_dynamic_variables": {},
        },
    }


@pytest.fixture
def sample_faq_payload():
    """Sample FAQ request payload."""
    return {
        "args": {
            "question": "How much does teeth whitening cost?",
        },
        "call_id": "call_test_faq",
    }
