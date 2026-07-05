"""
Google Sheets service for reading/writing appointment data.

Uses gspread with a GCP service account for authentication.
Wraps all Sheets I/O with error handling and logging.
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import Optional
from app.config import settings
from app.utils.logger import logger

# Required OAuth scopes for Sheets + Drive access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Sheet tab names
APPOINTMENTS_SHEET = "Appointments"
CALL_LOGS_SHEET = "Call Logs"
FAQ_SHEET = "FAQ Knowledge Base"


class SheetsService:
    """
    Google Sheets CRUD operations for the dental clinic.

    Manages three sheets:
    - Appointments: Booking records
    - Call Logs: Call metadata and analysis
    - FAQ Knowledge Base: Frequently asked questions
    """

    def __init__(self):
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None
        
        # --- Local In-Memory Fallback DB ---
        self.use_mock = False
        self._mock_appointments = []
        self._mock_call_logs = []
        self._mock_faqs = [
            {
                "ID": 1,
                "Category": "services",
                "Question": "What dental services do you offer?",
                "Answer": "We offer Dental Cleaning, Root Canal Treatment, Teeth Whitening, Braces Consultation, Tooth Extraction, and General Dental Consultation.",
                "Keywords": "services, offer, provide, do, treatments, procedures",
            },
            {
                "ID": 2,
                "Category": "hours",
                "Question": "What are your working hours?",
                "Answer": "We are open Monday through Saturday from 9 AM to 6 PM. We are closed on Sundays.",
                "Keywords": "hours, open, close, working, schedule, time, when",
            },
            {
                "ID": 13,
                "Category": "payment",
                "Question": "What payment methods do you accept?",
                "Answer": "We accept cash, all major credit and debit cards, and most dental insurance plans. We also offer flexible payment plans.",
                "Keywords": "payment, pay, credit, debit, card, cash, methods, plans",
            },
            {
                "ID": 16,
                "Category": "pricing",
                "Question": "What is your consultation fee?",
                "Answer": "Our standard consultation fee is ₹500. This covers a comprehensive oral examination by our dentist.",
                "Keywords": "consultation fee, consult fee, doctor fee, exam fee, checkup cost",
            },
            {
                "ID": 22,
                "Category": "walkins",
                "Question": "Do you accept walk-in patients?",
                "Answer": "We do accept walk-in patients based on availability, but wait times can vary. We highly recommend booking an appointment.",
                "Keywords": "walk in, walkins, walk-in, without appointment, just walk in",
            },
            {
                "ID": 9,
                "Category": "location",
                "Question": "Where is your clinic located?",
                "Answer": "Our clinic is located at 123 Dental Ave, Suite 100, New York, NY 10001. We offer free visitor parking.",
                "Keywords": "location, where, address, directions, find, located, parking",
            },
            {
                "ID": 7,
                "Category": "emergency",
                "Question": "Do you handle dental emergencies?",
                "Answer": "Yes, we accommodate dental emergencies during our working hours. If you are in severe pain, please call us immediately.",
                "Keywords": "emergency, urgent, pain, severe, broken, swelling",
            }
        ]

    def _get_client(self) -> gspread.Client:
        """Lazily initialize the gspread client."""
        if self._client is None:
            try:
                creds = Credentials.from_service_account_file(
                    settings.google_service_account_file,
                    scopes=SCOPES,
                )
                self._client = gspread.authorize(creds)
                logger.debug("DEBUG - Google Sheets initialized")
            except Exception as e:
                logger.error(f"ERROR - Failed to initialize Google Sheets client: {e}")
                raise
        return self._client

    def _get_spreadsheet(self) -> Optional[gspread.Spreadsheet]:
        """Get the configured spreadsheet."""
        if self.use_mock:
            return None
        if self._spreadsheet is None:
            try:
                client = self._get_client()
                self._spreadsheet = client.open_by_key(settings.google_sheets_spreadsheet_id)
                logger.info(f"INFO - Connected to spreadsheet: {self._spreadsheet.title}")
            except Exception as e:
                logger.warning(
                    f"WARNING - Failed to connect to Google Sheets: {e}. "
                    "Falling back to local in-memory mock database for development."
                )
                self.use_mock = True
                self._spreadsheet = None
        return self._spreadsheet

    def _get_worksheet(self, sheet_name: str) -> Optional[gspread.Worksheet]:
        """Get a specific worksheet by name."""
        if self.use_mock:
            return None
        spreadsheet = self._get_spreadsheet()
        if self.use_mock or spreadsheet is None:
            return None
        try:
            return spreadsheet.worksheet(sheet_name)
        except Exception as e:
            logger.warning(
                f"WARNING - Worksheet '{sheet_name}' not found: {e}. "
                "Falling back to local in-memory mock database."
            )
            self.use_mock = True
            return None

    # ================================================================
    # Appointments
    # ================================================================

    def append_appointment(self, row_data: list) -> bool:
        """
        Append a new appointment row to the Appointments sheet.

        Args:
            row_data: List of values matching the Appointments columns:
                [booking_id, name, phone, email, service, date, time,
                 status, booked_via, call_id, created_at]

        Returns:
            True if the row was appended successfully.
        """
        if self.use_mock or self._get_spreadsheet() is None:
            record = {
                "Booking ID": row_data[0],
                "Customer Name": row_data[1],
                "Phone": row_data[2],
                "Email": row_data[3],
                "Service": row_data[4],
                "Date": row_data[5],
                "Time": row_data[6],
                "Status": row_data[7],
                "Booked Via": row_data[8],
                "Call ID": row_data[9],
                "Created At": row_data[10],
            }
            self._mock_appointments.append(record)
            logger.info(f"INFO - [MOCK DB] Appointment created: {record['Booking ID']} for {record['Customer Name']}")
            return True

        try:
            worksheet = self._get_worksheet(APPOINTMENTS_SHEET)
            worksheet.append_row(row_data, value_input_option="USER_ENTERED")
            logger.info(f"INFO - Appointment created: {row_data[0]} for {row_data[1]}")
            return True
        except Exception as e:
            logger.error(f"ERROR - Failed to append appointment: {e}")
            return False

    def get_appointments_by_date(self, date_str: str) -> list[dict]:
        """
        Retrieve all appointments for a specific date.

        Args:
            date_str: Date string in YYYY-MM-DD format.

        Returns:
            List of appointment dicts (column_header -> value).
        """
        if self.use_mock or self._get_spreadsheet() is None:
            return [
                appt for appt in self._mock_appointments
                if appt.get("Date") == date_str
                and appt.get("Status") != "Cancelled"
            ]

        try:
            worksheet = self._get_worksheet(APPOINTMENTS_SHEET)
            all_records = worksheet.get_all_records()
            return [
                record for record in all_records
                if record.get("Date") == date_str
                and record.get("Status") != "Cancelled"
            ]
        except Exception as e:
            logger.error(f"ERROR - Failed to fetch appointments for {date_str}: {e}")
            return []

    def get_booked_times_for_date(self, date_str: str) -> list[str]:
        """
        Get list of already-booked time slots for a given date.

        Args:
            date_str: Date string in YYYY-MM-DD format.

        Returns:
            List of booked time strings (e.g., ["10:00 AM", "2:00 PM"]).
        """
        appointments = self.get_appointments_by_date(date_str)
        return [appt.get("Time", "") for appt in appointments if appt.get("Time")]

    def count_appointments_for_date(self, date_str: str) -> int:
        """Count non-cancelled appointments for a date."""
        return len(self.get_appointments_by_date(date_str))

    def get_next_booking_sequence(self, date_str: str) -> int:
        """
        Get the next sequential booking number for a date.

        Returns:
            Next sequence number (1-based).
        """
        count = self.count_appointments_for_date(date_str)
        return count + 1

    # ================================================================
    # Call Logs
    # ================================================================

    def log_call(self, row_data: list) -> bool:
        """
        Append a call log entry to the Call Logs sheet.

        Args:
            row_data: List of values matching Call Logs columns:
                [call_id, direction, from_number, start_time, end_time,
                 duration_sec, outcome, sentiment, summary, transferred]

        Returns:
            True if the row was appended successfully.
        """
        if self.use_mock or self._get_spreadsheet() is None:
            record = {
                "Call ID": row_data[0],
                "Direction": row_data[1],
                "From Number": row_data[2],
                "Start Time": row_data[3],
                "End Time": row_data[4],
                "Duration (sec)": row_data[5],
                "Outcome": row_data[6],
                "Sentiment": row_data[7],
                "Summary": row_data[8],
                "Transferred": row_data[9],
            }
            self._mock_call_logs.append(record)
            logger.info(f"INFO - [MOCK DB] Call logged: {record['Call ID']}")
            return True

        try:
            worksheet = self._get_worksheet(CALL_LOGS_SHEET)
            worksheet.append_row(row_data, value_input_option="USER_ENTERED")
            logger.info(f"INFO - Call logged: {row_data[0]}")
            return True
        except Exception as e:
            logger.error(f"ERROR - Failed to log call: {e}")
            return False

    def update_call_log(self, call_id: str, updates: dict) -> bool:
        """
        Update an existing call log entry with additional data (e.g., post-analysis).

        Args:
            call_id: The Retell call ID to find.
            updates: Dict of column_name -> new_value to update.

        Returns:
            True if the update succeeded.
        """
        if self.use_mock or self._get_spreadsheet() is None:
            for record in self._mock_call_logs:
                if record.get("Call ID") == call_id:
                    record.update(updates)
                    logger.info(f"INFO - [MOCK DB] Call log updated: {call_id}")
                    return True
            logger.warning(f"WARNING - [MOCK DB] Call ID {call_id} not found in call logs")
            return False

        try:
            worksheet = self._get_worksheet(CALL_LOGS_SHEET)
            all_records = worksheet.get_all_records()
            headers = worksheet.row_values(1)

            for idx, record in enumerate(all_records):
                if record.get("Call ID") == call_id:
                    row_number = idx + 2  # +1 for header, +1 for 1-indexed
                    for col_name, value in updates.items():
                        if col_name in headers:
                            col_number = headers.index(col_name) + 1
                            worksheet.update_cell(row_number, col_number, value)
                    logger.info(f"INFO - Call log updated: {call_id}")
                    return True

            logger.warning(f"WARNING - Call ID {call_id} not found in call logs")
            return False
        except Exception as e:
            logger.error(f"ERROR - Failed to update call log for {call_id}: {e}")
            return False

    # ================================================================
    # FAQ Knowledge Base
    # ================================================================

    def get_all_faqs(self) -> list[dict]:
        """
        Retrieve all FAQ entries from the FAQ Knowledge Base sheet.

        Returns:
            List of FAQ dicts with keys: ID, Category, Question, Answer, Keywords.
        """
        if self.use_mock or self._get_spreadsheet() is None:
            logger.info(f"INFO - [MOCK DB] Loaded {len(self._mock_faqs)} FAQ entries")
            return self._mock_faqs

        try:
            worksheet = self._get_worksheet(FAQ_SHEET)
            records = worksheet.get_all_records()
            logger.info(f"INFO - Loaded {len(records)} FAQ entries")
            return records
        except Exception as e:
            logger.error(f"ERROR - Failed to load FAQs: {e}")
            return []


# Singleton instance
sheets_service = SheetsService()
