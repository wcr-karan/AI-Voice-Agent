# RetellAI Setup Guide

Step-by-step instructions to configure the RetellAI agent for QuensultingAI Dental Clinic.

## Prerequisites

- A RetellAI account ([sign up here](https://www.retellai.com/))
- A deployed FastAPI backend with a public URL (see [Deployment Guide](./deployment_guide.md))

---

## Step 1: Create a Retell Agent

1. Log in to the [Retell Dashboard](https://app.retellai.com/)
2. Click **"Create Agent"** → Select **"Conversation Flow"** type
3. Name it: `QuensultingAI Dental Receptionist`
4. Select voice: `Adrian` (or any professional, warm voice)
5. Set language: `English (US)`

## Step 2: Import the Conversation Flow

1. In the agent settings, navigate to the **Conversation Flow** editor
2. You can either:
   - **Build manually** using the node specifications in `retell/conversation_flow.json` as a reference
   - **Import via API** using the Retell REST API:
     ```bash
     curl -X POST https://api.retellai.com/v2/create-conversation-flow \
       -H "Authorization: Bearer YOUR_RETELL_API_KEY" \
       -H "Content-Type: application/json" \
       -d @retell/conversation_flow.json
     ```

## Step 3: Configure Function Nodes

For each Function Node, configure the API endpoint to point to your deployed backend:

| Function Node | Endpoint URL |
|---|---|
| CheckAvailability | `https://your-backend.com/check-availability` |
| BookAppointment | `https://your-backend.com/book-appointment` |
| LookupFAQ | `https://your-backend.com/check-faq` |
| TransferCall | `https://your-backend.com/transfer-call` |

### Function Node Configuration

For each Function Node:
1. Set **Method**: `POST`
2. Set **URL**: Your backend endpoint
3. Configure **Parameters** to pass the dynamic variables (see `conversation_flow.json`)
4. Enable **"Speak during execution"** for availability and booking nodes
5. Map the **response fields** to dynamic variables

## Step 4: Configure Agent Settings

Apply these settings from `retell/agent_config.json`:

| Setting | Value | Reason |
|---|---|---|
| Responsiveness | 0.7 | Natural conversation pace |
| Interruption Sensitivity | 0.7 | Allows natural barge-in |
| Voice Speed | 1.0 | Normal speaking rate |
| Backchannel | Disabled | Prevents "uh-huh" during data collection |
| End Call After Silence | 15 seconds | Ends call if caller is silent |
| Max Call Duration | 10 minutes | Prevents runaway calls |

## Step 5: Set Up Webhook

1. In agent settings, find **Webhook URL**
2. Set it to: `https://your-backend.com/webhook`
3. Enable events: `call_started`, `call_ended`, `call_analyzed`
4. Copy the **Webhook Secret** to your `.env` file as `RETELL_WEBHOOK_SECRET`

## Step 6: Configure Post-Call Analysis

1. Enable **Post-Call Analysis**
2. Add custom analysis fields:
   - `call_summary` (string): "Summarize the call in 1-2 sentences"
   - `user_sentiment` (enum: positive/neutral/negative): "Overall caller sentiment"

## Step 7: Provision Phone Number

1. Go to **Phone Numbers** in the dashboard
2. Click **"Buy Number"** or **"Import Number"**
3. Select your preferred area code
4. Assign the phone number to your agent
5. Copy the number to your `.env` as `CLINIC_PHONE`

## Step 8: Configure Call Transfer

1. In agent settings, enable **Call Transfer**
2. Set the transfer phone number to your front desk line
3. This is the number used when the agent transfers to a human

## Step 9: Test the Agent

1. Use the **"Test Call"** button in the Retell dashboard
2. Run through these scenarios:
   - Book an appointment (all services)
   - Ask FAQ questions
   - Request to speak to a human
   - Give unclear/ambiguous requests
   - Interrupt the agent mid-sentence

## Step 10: Go Live

1. Verify all Function Nodes return valid responses
2. Verify webhook events are being received
3. Test with a real phone call to the provisioned number
4. Monitor the first few calls in the Retell dashboard

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Function Node times out | Ensure your backend responds within 10 seconds |
| Agent reads JSON aloud | Disable "Speak during execution" on the Function Node |
| Webhook not received | Verify URL is publicly accessible, check signature secret |
| Agent doesn't transfer | Ensure call transfer is enabled and number is configured |
