import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# The scope for the Gemini API
SCOPES = ['https://www.googleapis.com/auth/generative-language.retriever']

# Ensure paths are absolute and relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(PROJECT_ROOT, 'token.json')
CLIENT_SECRET_PATH = os.path.join(PROJECT_ROOT, 'client_secret.json')

def load_creds():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = run_login_flow()
        else:
            creds = run_login_flow()
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def run_login_flow():
    if not os.path.exists(CLIENT_SECRET_PATH):
        raise FileNotFoundError(f"Please download '{CLIENT_SECRET_PATH}' from Google Cloud Console.")
    
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def is_logged_in():
    return os.path.exists(TOKEN_PATH)
