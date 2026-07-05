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
    with patch("app.middleware.signature.verify_retell_signature") as mock_verify:
        # Return a valid JSON body by default
        mock_verify.return_value = b'{}'
        yield TestClient(app)


@pytest.fixture
def mock_sheets_service():
    """Mock the Google Sheets service."""
    with patch("app.services.sheets_service.sheets_service") as mock:
        mock.append_appointment.return_value = True
        mock.get_booked_times_for_date.return_value = []
        mock.get_next_booking_sequence.return_value = 1
        mock.log_call.return_value = True
        mock.get_all_faqs.return_value = [
            {
                "ID": 1,
                "Category": "pricing",
                "Question": "How much does teeth whitening cost?",
                "Answer": "Our teeth whitening starts at $299.",
                "Keywords": "whitening, cost, price, how much",
            },
            {
                "ID": 2,
                "Category": "hours",
                "Question": "What are your working hours?",
                "Answer": "We are open Monday through Saturday, 9 AM to 6 PM.",
                "Keywords": "hours, open, working, schedule, time",
            },
        ]
        yield mock


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
def sample_webhook_payload():
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
def sample_faq_payload():
    """Sample FAQ request payload."""
    return {
        "args": {
            "question": "How much does teeth whitening cost?",
        },
        "call_id": "call_test_789",
    }
