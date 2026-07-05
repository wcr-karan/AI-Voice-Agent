"""
Tests for the booking endpoint and booking service.
"""

import json
from unittest.mock import patch


class TestBookingEndpoint:
    """Test POST /book-appointment."""

    @patch("app.api.booking.email_service")
    @patch("app.api.booking.booking_service")
    def test_successful_booking(self, mock_booking_svc, mock_email, client, sample_booking_payload):
        """Successful booking returns confirmed status."""
        test_client, mocks = client
        mocks["booking"].return_value = json.dumps(sample_booking_payload).encode()

        from app.models.appointment import BookingResponse
        mock_booking_svc.book_appointment.return_value = BookingResponse(
            booking_id="BK-20270705-001",
            status="confirmed",
            message="Appointment confirmed for John Smith.",
        )

        response = test_client.post("/book-appointment")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "confirmed"
        assert data["result"]["booking_id"] == "BK-20270705-001"

    @patch("app.api.booking.booking_service")
    def test_booking_with_invalid_service(self, mock_booking_svc, client, sample_booking_payload):
        """Invalid service type returns failed status."""
        test_client, mocks = client
        sample_booking_payload["args"]["service_type"] = "Brain Surgery"
        mocks["booking"].return_value = json.dumps(sample_booking_payload).encode()

        from app.models.appointment import BookingResponse
        mock_booking_svc.book_appointment.return_value = BookingResponse(
            status="failed",
            message="Brain Surgery is not one of our available services.",
        )

        response = test_client.post("/book-appointment")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "failed"

    @patch("app.api.booking.booking_service")
    def test_booking_slot_conflict(self, mock_booking_svc, client, sample_booking_payload):
        """Slot conflict returns conflict status with alternatives."""
        test_client, mocks = client
        mocks["booking"].return_value = json.dumps(sample_booking_payload).encode()

        from app.models.appointment import BookingResponse
        mock_booking_svc.book_appointment.return_value = BookingResponse(
            status="conflict",
            message="10 AM is already booked. Next available: 11 AM, 2 PM.",
        )

        response = test_client.post("/book-appointment")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "conflict"


class TestBookingService:
    """Test booking_service business logic."""

    @patch("app.services.booking_service.sheets_service")
    def test_validates_service_type(self, mock_sheets):
        """Rejects invalid service types."""
        from app.services.booking_service import booking_service

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Brain Surgery",
            appointment_date_str="2027-07-05",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "not one of our available services" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_rejects_past_dates(self, mock_sheets):
        """Rejects dates in the past."""
        from app.services.booking_service import booking_service

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str="2020-01-01",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "passed" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_rejects_sunday(self, mock_sheets):
        """Rejects bookings on Sunday."""
        from app.services.booking_service import booking_service

        # Find a future Sunday
        from datetime import date, timedelta
        today = date.today()
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        next_sunday = today + timedelta(days=days_until_sunday)

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str=next_sunday.strftime("%Y-%m-%d"),
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "Sunday" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_rejects_outside_hours(self, mock_sheets):
        """Rejects times outside working hours."""
        from app.services.booking_service import booking_service

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str="2027-07-05",
            appointment_time_str="7:00 AM",
        )
        assert result.status == "failed"
        assert "outside our working hours" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_invalid_email(self, mock_sheets):
        """Rejects invalid email format."""
        from app.services.booking_service import booking_service

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="invalid-email",
            service_type="Dental Cleaning",
            appointment_date_str="2027-07-05",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "email address format" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_invalid_phone(self, mock_sheets):
        """Rejects invalid phone number format."""
        from app.services.booking_service import booking_service

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="not-a-phone",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str="2027-07-05",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "phone number format" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_duplicate_booking(self, mock_sheets):
        """Rejects duplicate booking on the same day for same service."""
        from app.services.booking_service import booking_service

        mock_sheets.get_appointments_by_date.return_value = [
            {
                "Email": "test@test.com",
                "Phone": "+1111111111",
                "Service": "Dental Cleaning",
                "Status": "Confirmed",
            }
        ]

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str="2027-07-05",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "already have an appointment booked" in result.message

    @patch("app.services.booking_service.sheets_service")
    def test_sheets_failure(self, mock_sheets):
        """Returns failed status when Sheets write fails."""
        from app.services.booking_service import booking_service

        mock_sheets.get_booked_times_for_date.return_value = []
        mock_sheets.get_next_booking_sequence.return_value = 1
        mock_sheets.append_appointment.return_value = False

        result = booking_service.book_appointment(
            customer_name="Test User",
            customer_phone="+1111111111",
            customer_email="test@test.com",
            service_type="Dental Cleaning",
            appointment_date_str="2027-07-05",
            appointment_time_str="10:00 AM",
        )
        assert result.status == "failed"
        assert "issue while booking" in result.message
