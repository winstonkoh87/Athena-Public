#!/usr/bin/env python3
"""
Calendar Agent (Bankai Module C)
Google Calendar Interface.
"""

import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

def get_service():
    """Authenticate and return Calendar service."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError("credentials.json not found. Run setup_calendar_auth.py")
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save credentials
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def list_events(n: int = 5) -> list[str]:
    """List upcoming n events."""
    try:
        service = get_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=n, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        output = []
        if not events:
            return ["No upcoming events found."]
            
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"{start}: {event['summary']}")
            
        return output
    except Exception as e:
        return [f"Error: {e}"]

def quick_add(text: str) -> str:
    """Quick add event (Natural Language)."""
    try:
        service = get_service()
        created_event = service.events().quickAdd(
            calendarId='primary',
            text=text
        ).execute()
        return f"Event created: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating event: {e}"

if __name__ == "__main__":
    # Test run
    print("Upcoming 3 events:")
    for e in list_events(3):
        print(e)
