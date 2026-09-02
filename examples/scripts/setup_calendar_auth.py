#!/usr/bin/env python3
"""
Calendar Auth Helper
Run this to generate token.json from credentials.json
"""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
ScriptDir = os.path.dirname(__file__)
TOKEN_PATH = os.path.join(ScriptDir, 'token.json')
CREDENTIALS_PATH = os.path.join(ScriptDir, 'credentials.json')

def main():
    print("🔐 Authenticating with Google...")
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print("❌ Error: credentials.json not found in .agent/scripts/")
                print("1. Go to Google Cloud Console")
                print("2. Create Project -> Enable Calendar API")
                print("3. Create Desktop Credential -> Download JSON")
                print("4. Rename to credentials.json and place in .agent/scripts/")
                return

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        print("✅ token.json generated!")
    else:
        print("✅ Already authenticated.")

if __name__ == '__main__':
    main()
