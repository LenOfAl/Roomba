import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = ["nairanirudh2309@gmail.com","allennellasorry@gmail.com","ananthananil8301@gmail.com"]
#our_email="allennellasorry@gmail.com" 

def gmailAuthenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port = 0)

    if not creds or not creds.valid :
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            help(creds)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)
        
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)
    
    return build ('gmail', 'v1', credentials=creds)
            
service = gmailAuthenticate()
