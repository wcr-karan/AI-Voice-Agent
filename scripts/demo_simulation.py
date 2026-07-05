#!/usr/bin/env python3
"""
QuensultingAI Dental Clinic — AI Voice Agent Demo Simulation.

Runs a series of mock REST requests to showcase the voice agent's API 
and backend integrations without needing an active telephone call.

Make sure the FastAPI server is running before executing this script:
    make dev  (or uvicorn app.main:app)
"""

import json
import urllib.request
import urllib.error
import sys
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  🚀 {title}")
    print("=" * 60)


def make_post_request(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-retell-signature": "dummy_signature_skipped_in_dev",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            print(f"   Detail: {error_body}")
        except Exception:
            pass
        return {}
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        print("\n💡 Is your FastAPI server running? Start it with 'make dev' or 'uvicorn app.main:app'")
        sys.exit(1)


def main():
    print("🦷 QuensultingAI Dental Voice Agent — Interactive Demo Simulation 🦷")
    print("This script simulates Retell AI's conversation engine communicating with your FastAPI backend.\n")

    # Check if server is running
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health") as response:
            health = json.loads(response.read().decode("utf-8"))
            print(f"🟢 Backend Status: {health.get('status')} (Environment: {health.get('environment')})")
    except Exception:
        print("🔴 Backend Server is not running.")
        print("💡 Please start the server using 'make dev' or 'uvicorn app.main:app --reload' and run this script again.")
        sys.exit(1)

    # ----------------------------------------------------
    # 1. Simulating FAQ Lookup
    # ----------------------------------------------------
    print_header("Step 1: FAQ Lookup Simulation")
    question = "Do you accept walk-in patients and what is the consultation fee?"
    print(f"📞 Caller asks: '{question}'")
    
    faq_payload = {
        "args": {"question": question},
        "call_id": "demo_call_faq_999",
    }
    faq_response = make_post_request("/check-faq", faq_payload)
    result = faq_response.get("result", {})
    if result.get("found"):
        print(f"🤖 Agent Response (via FAQ database):")
        print(f"   Category: {result.get('category')}")
        print(f"   Answer:   {result.get('message')}")
    else:
        print(f"🤖 Agent Response: {result.get('message')}")

    # ----------------------------------------------------
    # 2. Simulating Check Availability
    # ----------------------------------------------------
    print_header("Step 2: Slot Availability Check")
    # Choose a future Monday or Tuesday
    future_date = date.today() + timedelta(days=2)
    if future_date.weekday() == 6:  # Skip Sunday
        future_date += timedelta(days=1)
    
    date_str = future_date.strftime("%Y-%m-%d")
    service = "Teeth Whitening"
    print(f"📞 Caller asks: 'Are there slots available for {service} on {date_str}?'")

    avail_payload = {
        "args": {
            "service_type": service,
            "preferred_date": date_str,
        },
        "call_id": "demo_call_booking_999",
    }
    avail_response = make_post_request("/check-availability", avail_payload)
    res = avail_response.get("result", {})
    print(f"🤖 Agent Checks Slots:")
    print(f"   Status:   {'Slots Available' if res.get('available') else 'Fully Booked'}")
    print(f"   Response: {res.get('message')}")

    # ----------------------------------------------------
    # 3. Simulating Appointment Booking
    # ----------------------------------------------------
    print_header("Step 3: Appointment Booking")
    print("📞 Caller confirms details: 'Karan Thakur, +1 555-0199, karan@example.com'")
    
    booking_payload = {
        "args": {
            "customer_name": "Karan Thakur",
            "customer_phone": "+1 555-0199",
            "customer_email": "karan@example.com",
            "service_type": service,
            "appointment_date": date_str,
            "appointment_time": "10:30 AM",
        },
        "call_id": "demo_call_booking_999",
    }
    booking_response = make_post_request("/book-appointment", booking_payload)
    book_res = booking_response.get("result", {})
    print("🤖 Agent Books Appointment & Triggers Confirmation Email:")
    print(f"   Status:            {book_res.get('status')}")
    print(f"   Booking Reference: {book_res.get('booking_id')}")
    print(f"   Speech Prompt:     {book_res.get('message')}")

    # ----------------------------------------------------
    # 4. Simulating Webhook logging (Post-Call)
    # ----------------------------------------------------
    print_header("Step 4: Webhook Logging (Call Ended)")
    print("📞 Call hangs up. Retell sends the 'call_ended' webhook event...")
    
    webhook_ended_payload = {
        "event": "call_ended",
        "call": {
            "call_id": "demo_call_booking_999",
            "call_type": "phone_call",
            "from_number": "+1 555-0199",
            "to_number": "+1 800-555-0100",
            "direction": "inbound",
            "start_timestamp": 1720164600000,
            "end_timestamp": 1720164780000,
            "duration_seconds": 180,
            "retell_llm_dynamic_variables": {
                "booking_id": book_res.get("booking_id"),
            },
        },
    }
    webhook_ended_response = make_post_request("/webhook", webhook_ended_payload)
    print(f"💻 Webhook response: {webhook_ended_response}")
    print("   ✓ Call record inserted into Google Sheets ('Call Logs' tab).")

    # ----------------------------------------------------
    # 5. Simulating Webhook analysis (Post-Call Analysis)
    # ----------------------------------------------------
    print_header("Step 5: Webhook Post-Call Analysis")
    print("💻 Retell completes call recording analysis and sends 'call_analyzed' event...")
    
    webhook_analyzed_payload = {
        "event": "call_analyzed",
        "call": {
            "call_id": "demo_call_booking_999",
            "call_type": "phone_call",
            "from_number": "+1 555-0199",
            "to_number": "+1 800-555-0100",
            "direction": "inbound",
            "call_analysis": {
                "call_summary": "Karan Thakur booked a Teeth Whitening appointment for 10:30 AM. He also inquired about walk-in guidelines.",
                "user_sentiment": "positive",
            },
        },
    }
    webhook_analyzed_response = make_post_request("/webhook", webhook_analyzed_payload)
    print(f"💻 Webhook response: {webhook_analyzed_response}")
    print("   ✓ Updated Google Sheets with sentiment ('positive') and call summary.")

    print("\n" + "=" * 60)
    print("🎉 DEMO SIMULATION COMPLETED SUCCESSFULLY!")
    print("Verify your Google Sheet and check your console logs to see the data flow.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
