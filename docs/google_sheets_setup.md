# Google Sheets Setup Guide

How to configure Google Sheets as the data layer for the voice agent.

---

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"New Project"** → Name it `quensultingai-voice-agent`
3. Wait for the project to be created

## Step 2: Enable Required APIs

1. Go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API**

## Step 3: Create a Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"Service Account"**
3. Name: `voice-agent-sheets`
4. Role: **Editor** (or a custom role with Sheets + Drive access)
5. Click **"Done"**
6. Click on the created service account
7. Go to **Keys** tab → **"Add Key"** → **"Create new key"** → **JSON**
8. Download the key file and save it as `service_account.json` in your project root

> ⚠️ **Never commit `service_account.json` to Git.** It's already in `.gitignore`.

## Step 4: Create the Google Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it: `QuensultingAI Dental Clinic — Voice Agent Data`
4. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
5. Add this ID to your `.env` file as `GOOGLE_SHEETS_SPREADSHEET_ID`

## Step 5: Share the Spreadsheet

1. Open the `service_account.json` file
2. Find the `client_email` field (looks like: `voice-agent-sheets@project.iam.gserviceaccount.com`)
3. In Google Sheets, click **"Share"**
4. Paste the service account email
5. Give it **"Editor"** access
6. Uncheck "Notify people" and click **"Share"**

## Step 6: Run the Setup Script

This creates the three required sheet tabs with formatted headers:

```bash
python scripts/setup_google_sheets.py
```

Expected output:
```
Setting up Google Sheets for QuensultingAI Dental Clinic...

  + Created sheet 'Appointments'
    Headers set: Booking ID, Customer Name, Phone, Email, ...
  + Created sheet 'Call Logs'
    Headers set: Call ID, Direction, From Number, ...
  + Created sheet 'FAQ Knowledge Base'
    Headers set: ID, Category, Question, Answer, Keywords
  - Removed empty 'Sheet1'

✅ Google Sheets setup complete!
```

## Step 7: Seed FAQ Data

Populate the FAQ sheet with initial dental clinic FAQs:

```bash
python scripts/seed_faq_data.py
```

This inserts 15 pre-written FAQ entries covering services, pricing, insurance, hours, and more.

---

## Sheet Structure

### Appointments

| Column | Example |
|---|---|
| Booking ID | BK-20260705-003 |
| Customer Name | John Smith |
| Phone | +1234567890 |
| Email | john@example.com |
| Service | Dental Cleaning |
| Date | 2026-07-05 |
| Time | 10:00 AM |
| Status | Confirmed |
| Booked Via | Voice Agent |
| Call ID | call_abc123 |
| Created At | 2026-07-02T18:30:00Z |

### Call Logs

| Column | Example |
|---|---|
| Call ID | call_abc123 |
| Direction | inbound |
| From Number | +1234567890 |
| Start Time | 2026-07-02T18:25:00Z |
| End Time | 2026-07-02T18:30:00Z |
| Duration (sec) | 300 |
| Outcome | appointment_booked |
| Sentiment | positive |
| Summary | Patient booked cleaning... |
| Transferred | No |

### FAQ Knowledge Base

| Column | Example |
|---|---|
| ID | 1 |
| Category | pricing |
| Question | How much does teeth whitening cost? |
| Answer | Our teeth whitening starts at $299... |
| Keywords | whitening, cost, price, how much |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `gspread.exceptions.SpreadsheetNotFound` | Verify the spreadsheet ID in `.env` |
| `google.auth.exceptions.DefaultCredentialsError` | Check `service_account.json` path |
| `gspread.exceptions.APIError: 403` | Share the spreadsheet with the service account email |
| `WorksheetNotFound` | Run `python scripts/setup_google_sheets.py` |
