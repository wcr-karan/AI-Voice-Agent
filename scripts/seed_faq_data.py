"""
Seed FAQ data — Populates the FAQ Knowledge Base sheet with initial entries.

Run after setup_google_sheets.py:
    python scripts/seed_faq_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sheets_service import sheets_service

FAQ_DATA = [
    {
        "id": 1,
        "category": "services",
        "question": "What dental services do you offer?",
        "answer": "We offer Dental Cleaning, Root Canal Treatment, Teeth Whitening, Braces Consultation, Tooth Extraction, and General Dental Consultation.",
        "keywords": "services, offer, provide, do, treatments, procedures",
    },
    {
        "id": 2,
        "category": "hours",
        "question": "What are your working hours?",
        "answer": "We are open Monday through Saturday from 9 AM to 6 PM. We are closed on Sundays.",
        "keywords": "hours, open, close, working, schedule, time, when",
    },
    {
        "id": 3,
        "category": "pricing",
        "question": "How much does a dental cleaning cost?",
        "answer": "Our dental cleaning starts at $99. The exact cost may vary depending on your specific needs. We recommend scheduling a General Dental Consultation for a personalized quote.",
        "keywords": "cleaning, cost, price, how much, fee, charge",
    },
    {
        "id": 4,
        "category": "pricing",
        "question": "How much does teeth whitening cost?",
        "answer": "Our professional teeth whitening treatment starts at $299. Results are typically visible after one session. Would you like to book a consultation to discuss options?",
        "keywords": "whitening, cost, price, how much, fee, bleaching, white",
    },
    {
        "id": 5,
        "category": "pricing",
        "question": "How much does a root canal cost?",
        "answer": "Root canal treatment typically ranges from $700 to $1,200 depending on the tooth and complexity. We recommend a General Dental Consultation first so our dentist can provide an accurate estimate.",
        "keywords": "root canal, cost, price, how much, fee",
    },
    {
        "id": 6,
        "category": "insurance",
        "question": "Do you accept dental insurance?",
        "answer": "Yes, we accept most major dental insurance plans. Please bring your insurance card to your appointment, and our front desk team can verify your coverage. For specific questions about your plan, please call our front desk.",
        "keywords": "insurance, accept, cover, coverage, plan, dental plan",
    },
    {
        "id": 7,
        "category": "emergency",
        "question": "Do you handle dental emergencies?",
        "answer": "Yes, we accommodate dental emergencies during our working hours. If you're experiencing severe pain, swelling, or a knocked-out tooth, please call us immediately and we'll fit you in as soon as possible.",
        "keywords": "emergency, urgent, pain, severe, broken, knocked, swelling",
    },
    {
        "id": 8,
        "category": "preparation",
        "question": "How should I prepare for my appointment?",
        "answer": "Please arrive 10 minutes early for check-in. Bring a valid photo ID and your insurance card if applicable. Let us know about any medications you're taking or allergies. For specific procedures, we'll provide preparation instructions when you book.",
        "keywords": "prepare, preparation, before, appointment, bring, ready",
    },
    {
        "id": 9,
        "category": "location",
        "question": "Where is your clinic located?",
        "answer": "Our clinic is conveniently located at 123 Dental Ave, Suite 100, New York, NY 10001. We offer easy parking and are accessible by public transportation. You'll receive detailed directions in your confirmation email.",
        "keywords": "location, where, address, directions, find, located, parking",
    },
    {
        "id": 10,
        "category": "cancellation",
        "question": "What is your cancellation policy?",
        "answer": "We kindly ask for at least 24 hours notice if you need to cancel or reschedule your appointment. Late cancellations or no-shows may be subject to a $50 fee. To cancel, please call our front desk.",
        "keywords": "cancel, cancellation, reschedule, policy, no show, change",
    },
    {
        "id": 11,
        "category": "services",
        "question": "How long does a dental cleaning take?",
        "answer": "A standard dental cleaning typically takes about 30 to 45 minutes. If it's your first visit, please allow a bit extra time for the initial examination.",
        "keywords": "cleaning, long, duration, time, take, how long, minutes",
    },
    {
        "id": 12,
        "category": "services",
        "question": "Do you offer braces for adults?",
        "answer": "Absolutely! We offer braces consultations for both adults and children. Our orthodontic options include traditional braces and clear aligners. Book a Braces Consultation to discuss the best option for you.",
        "keywords": "braces, adult, adults, orthodontic, clear, aligners, invisalign",
    },
    {
        "id": 13,
        "category": "payment",
        "question": "What payment methods do you accept?",
        "answer": "We accept cash, all major credit and debit cards, and most dental insurance plans. We also offer flexible payment plans for larger procedures. Speak with our front desk for more details.",
        "keywords": "payment, pay, credit, debit, card, cash, methods, plans, financing",
    },
    {
        "id": 14,
        "category": "services",
        "question": "Is teeth whitening safe?",
        "answer": "Yes, professional teeth whitening performed by our dental team is completely safe. We use FDA-approved whitening agents and customize the treatment to your sensitivity level. Some patients may experience mild temporary sensitivity, which resolves quickly.",
        "keywords": "whitening, safe, safety, side effects, sensitive, sensitivity",
    },
    {
        "id": 15,
        "category": "first_visit",
        "question": "What happens during a first visit or general dental consultation?",
        "answer": "During your first visit, our dentist will perform a comprehensive oral examination, take any necessary X-rays, discuss your dental history, and create a personalized treatment plan. The visit typically takes about 45 minutes to an hour.",
        "keywords": "first visit, general dental consultation, general consultation, new patient, what happens, exam, examination",
    },
    {
        "id": 16,
        "category": "pricing",
        "question": "What is your consultation fee?",
        "answer": "Our standard consultation fee is ₹500. This covers a comprehensive oral examination by our dentist. Any additional treatments, X-rays, or specialized consultations will be detailed and charged separately.",
        "keywords": "consultation fee, consult fee, doctor fee, exam fee, checkup cost, how much checkup",
    },
    {
        "id": 17,
        "category": "parking",
        "question": "Is parking available at the clinic?",
        "answer": "Yes, we have free visitor parking available directly in front of the clinic. There is also ample street parking and a public parking garage within a short 2-minute walking distance.",
        "keywords": "parking, park, car, vehicle, visitor parking, free parking",
    },
    {
        "id": 18,
        "category": "pediatric",
        "question": "Do you treat children or offer pediatric dentistry?",
        "answer": "Yes, we treat patients of all ages, including children! We strive to make their dental visits fun and stress-free. We recommend scheduling their first checkup by their first birthday.",
        "keywords": "children, child, kids, pediatric, kid, toddler, pediatric dentistry",
    },
    {
        "id": 19,
        "category": "services",
        "question": "How long does a root canal treatment take?",
        "answer": "A root canal treatment typically takes between 60 to 90 minutes. Depending on the complexity and tooth location, it may sometimes require two sessions to complete the treatment.",
        "keywords": "root canal duration, root canal time, how long root canal, root canal take",
    },
    {
        "id": 20,
        "category": "cancellation",
        "question": "How can I reschedule my appointment?",
        "answer": "You can reschedule your appointment by calling our front desk team at least 24 hours before your slot. This allows us to offer the time to other patients who need care.",
        "keywords": "reschedule, change time, move appointment, change date",
    },
    {
        "id": 21,
        "category": "hours",
        "question": "Is the clinic open on Sundays?",
        "answer": "No, the clinic is closed on Sundays. Our working hours are Monday through Saturday, 9 AM to 6 PM.",
        "keywords": "sunday, sundays, weekend, open sunday, closed sunday",
    },
    {
        "id": 22,
        "category": "walkins",
        "question": "Do you accept walk-in patients?",
        "answer": "We do accept walk-in patients based on availability, but wait times can vary. We highly recommend booking an appointment in advance to secure your preferred slot.",
        "keywords": "walk in, walkins, walk-in, without appointment, just walk in",
    },
    {
        "id": 23,
        "category": "services",
        "question": "How long does a tooth extraction take?",
        "answer": "A simple tooth extraction typically takes about 30 to 45 minutes. More complex or surgical extractions may take longer. We ensure you are fully comfortable and numb throughout the process.",
        "keywords": "extraction duration, extraction time, how long extraction, tooth pull, pull tooth",
    },
    {
        "id": 24,
        "category": "payment",
        "question": "What payment types do you accept?",
        "answer": "We accept cash, all major credit and debit cards (Visa, MasterCard, American Express), mobile payment apps, and dental insurance. We also offer interest-free payment plans for select treatments.",
        "keywords": "accepted payment, payment types, card, credit card, cash only, checks",
    },
    {
        "id": 25,
        "category": "contact",
        "question": "What is your clinic's contact information?",
        "answer": "You can call us directly at our phone number or email us at appointments@quensultingai.com. We are located at 123 Dental Ave, Suite 100, New York, NY 10001.",
        "keywords": "contact, phone, email, number, address, call, get in touch",
    },
]


def seed_faqs():
    """Write FAQ entries to the FAQ Knowledge Base sheet."""
    worksheet = sheets_service._get_worksheet("FAQ Knowledge Base")

    rows = []
    for faq in FAQ_DATA:
        rows.append([
            faq["id"],
            faq["category"],
            faq["question"],
            faq["answer"],
            faq["keywords"],
        ])

    # Write all rows starting at A2 (after headers)
    if rows:
        worksheet.update(f"A2:E{len(rows) + 1}", rows, value_input_option="USER_ENTERED")

    print(f"✅ Seeded {len(rows)} FAQ entries to Google Sheets")


if __name__ == "__main__":
    print("Seeding FAQ data for QuensultingAI Dental Clinic...\n")
    seed_faqs()
