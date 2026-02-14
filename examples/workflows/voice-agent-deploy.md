---created: 2026-01-02
last_updated: 2026-01-30
---

---description: Deploy AI Voice Agents (ElevenLabs + Twilio)
created: 2026-01-02
last_updated: 2026-01-02
---

# Voice Agent Deployment Protocol

> **Purpose**: Deploy 24/7 Voice Agents for inbound/outbound calls using the "Paul James Stack".
> **Source**: CS-203
> **Value**: Replace $4k/mo human receptionist with ~$50/mo AI.

## Phase 1: Prerequisites

1. **ElevenLabs Account**: Creator Tier+ (for conversational AI).
2. **Twilio Account**: For phone number ($1/mo).
3. **Vapi.ai (Optional)**: If ElevenLabs native is not enough.

## Phase 2: Configuration (ElevenLabs)

1. **Create Agent**: Go to ElevenLabs -> Conversational AI -> Create.
2. **Select Voice**: Choose a high-quality voice (e.g., "Rachel").
3. **Prompting**:
    > "You are [Name], a receptionist for [Business]. Your goal is to book appointments.
    > Keep answers short (under 10 words).
    > If user says [X], ask [Y]."
4. **Knowledge Base**: Upload PDF of FAQs / Pricing.

## Phase 3: Telephony Connection

1. **Buy Number**: In Twilio, buy a local number.
2. **Webhook Sync**:
    - In ElevenLabs: Get "SIP URI" or "Twilio Config".
    - In Twilio: Set "Voice Webhook" to the ElevenLabs endpoint.

## Phase 4: Automation (Make.com)

**Goal**: When a call ends, data goes somewhere (CRM/Sheet).

1. **Trigger**: ElevenLabs "Call Ended".
2. **Action**: Parse JSON transcript.
3. **Destination**: Add row to Google Sheet or Card to Trello.

## Phase 5: Testing

1. **Latency Test**: Ensure <1000ms delay.
2. **Interrupt Test**: Speak over the AI. Does it stop?
3. **Hallucination Test**: Ask "What is the square root of a banana?" (Should refuse/pivot).

## Tags

# voice-agents #elevenlabs #automation #twilio
