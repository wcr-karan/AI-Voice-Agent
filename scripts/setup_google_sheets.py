"""
Setup Google Sheets — Creates the required sheet tabs with headers.

Run this once after creating your Google Spreadsheet:
    python scripts/setup_google_sheets.py

Prerequisites:
    - service_account.json in project root
    - GOOGLE_SHEETS_SPREADSHEET_ID in .env
    - Spreadsheet shared with service account email
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sheets_service import sheets_service

# Sheet definitions with headers
SHEETS = {
    "Appointments": [
        "Booking ID",
        "Customer Name",
        "Phone",
        "Email",
        "Service",
        "Date",
        "Time",
        "Status",
        "Booked Via",
        "Call ID",
        "Created At",
    ],
    "Call Logs": [
        "Call ID",
        "Direction",
        "From Number",
        "Start Time",
        "End Time",
        "Duration (sec)",
        "Outcome",
        "Sentiment",
        "Summary",
        "Transferred",
    ],
    "FAQ Knowledge Base": [
        "ID",
        "Category",
        "Question",
        "Answer",
        "Keywords",
    ],
}


def setup_sheets():
    """Create sheet tabs and set headers."""
    spreadsheet = sheets_service._get_spreadsheet()

    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]

    for sheet_name, headers in SHEETS.items():
        if sheet_name in existing_sheets:
            print(f"  ✓ Sheet '{sheet_name}' already exists")
            ws = spreadsheet.worksheet(sheet_name)
        else:
            ws = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
            print(f"  + Created sheet '{sheet_name}'")

        # Set headers in row 1
        ws.update("A1", [headers])

        # Bold + freeze header row
        ws.format("A1:Z1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.93, "blue": 0.98},
        })
        ws.freeze(rows=1)

        print(f"    Headers set: {', '.join(headers)}")

    # Remove default "Sheet1" if it exists and is empty
    if "Sheet1" in existing_sheets:
        try:
            default_sheet = spreadsheet.worksheet("Sheet1")
            if default_sheet.row_count <= 1:
                spreadsheet.del_worksheet(default_sheet)
                print("  - Removed empty 'Sheet1'")
        except Exception:
            pass

    print("\n✅ Google Sheets setup complete!")


if __name__ == "__main__":
    print("Setting up Google Sheets for QuensultingAI Dental Clinic...\n")
    setup_sheets()
