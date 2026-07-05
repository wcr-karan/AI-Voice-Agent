"""
Tests for the availability endpoint.
"""

import json
from unittest.mock import patch


class TestAvailabilityEndpoint:
    """Test POST /check-availability."""

    @patch("app.api.availability.booking_service")
    def test_available_slots(self, mock_svc, client, sample_availability_payload):
        """Returns available slots for a valid date."""
        test_client, mocks = client
        mocks["availability"].return_value = json.dumps(sample_availability_payload).encode()

        mock_svc.check_availability.return_value = {
            "available": True,
            "slots": ["9:00 AM", "10:00 AM", "2:00 PM"],
            "message": "We have 3 available slots.",
        }

        response = test_client.post("/check-availability")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["available"] is True
        assert len(data["result"]["slots"]) == 3

    @patch("app.api.availability.booking_service")
    def test_no_available_slots(self, mock_svc, client, sample_availability_payload):
        """Returns empty slots when fully booked."""
        test_client, mocks = client
        mocks["availability"].return_value = json.dumps(sample_availability_payload).encode()

        mock_svc.check_availability.return_value = {
            "available": False,
            "slots": [],
            "message": "We're fully booked on that day.",
        }

        response = test_client.post("/check-availability")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["available"] is False
        assert data["result"]["slots"] == []


class TestDatetimeHelpers:
    """Test datetime utility functions."""

    def test_generate_time_slots_weekday(self):
        """Generates correct slots for a weekday."""
        from app.utils.datetime_helpers import generate_time_slots
        from datetime import date

        # Monday July 7, 2025
        slots = generate_time_slots(date(2025, 7, 7))
        assert len(slots) > 0
        assert slots[0] == "9:00 AM"

    def test_generate_time_slots_sunday(self):
        """Returns empty list for Sunday."""
        from app.utils.datetime_helpers import generate_time_slots
        from datetime import date

        # Sunday July 6, 2025
        slots = generate_time_slots(date(2025, 7, 6))
        assert slots == []

    def test_parse_date_multiple_formats(self):
        """Parses dates in multiple formats."""
        from app.utils.datetime_helpers import parse_date
        from datetime import date

        assert parse_date("2026-07-05") == date(2026, 7, 5)
        assert parse_date("07/05/2026") == date(2026, 7, 5)
        assert parse_date("July 5, 2026") == date(2026, 7, 5)

    def test_parse_date_invalid(self):
        """Returns None for unparseable dates."""
        from app.utils.datetime_helpers import parse_date

        assert parse_date("not a date") is None
        assert parse_date("") is None

    def test_parse_time_multiple_formats(self):
        """Parses times in multiple formats."""
        from app.utils.datetime_helpers import parse_time
        from datetime import time

        result = parse_time("10:00 AM")
        assert result == time(10, 0)

        result = parse_time("2:30 PM")
        assert result == time(14, 30)

    def test_generate_booking_id(self):
        """Generates correctly formatted booking IDs."""
        from app.utils.datetime_helpers import generate_booking_id
        from datetime import date

        bid = generate_booking_id(date(2026, 7, 5), 3)
        assert bid == "BK-20260705-003"

    def test_format_date_for_speech(self):
        """Formats dates for natural speech."""
        from app.utils.datetime_helpers import format_date_for_speech
        from datetime import date

        result = format_date_for_speech(date(2026, 7, 5))
        assert "July" in result
        assert "5th" in result
