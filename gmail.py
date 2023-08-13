import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64

keywords = ["application has been dropped","lost", "viva", "found", "sale", "ticket", "taxi", "airport", "station", "cab", "purchase", "phd open","snake"]

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = ["nairanirudh2309@gmail.com","allennellasorry@gmail.com","ananthananil8301@gmail.com"]
#our_email="allennellasorry@gmail.com" 

def gmailAuthenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid :
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            help(creds)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)
        
        with open("token.pickle", "wb") as token:
            pickle.dump(creds,token)
    return build('gmail', 'v1', credentials=creds)
            
service = gmailAuthenticate()



def search_mails(service,query):
    result=service.users().messages().list(userId='me').execute()
    messages=[]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token=result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query,labelIds=['INBOX'], pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    #     break
    return messages

messages=search_mails(service,"is:unread")


def read_mail(service,messages):
    ids=[]
    message_count=0
    for message in messages: 
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        message_count= message_count + 1
        email_data= msg['payload']['headers']
        for values in email_data:
           name = values["name"]
           if name == "From":
               from_name = values ["value"]
            #    print(from_name)
               subject= [j['value'] for j in email_data if j["name"]=="Subject"]
               if check_sub(subject):
                   ids.append(msg['id'])
    print(ids)
    return ids
        # print(msg["payload"])
        # try:
        #     for p in msg["payload"]["parts"]:
        #         if p["mimeType"] in ["text/plain"]:
        #             data = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
        #             print(data)
        # except Exception as e:
        #     pass

def check_sub(subject):
    for s in subject:
        s=s.lower()
        for keyword in keywords:
            if keyword in s:
                print(subject)
                return True
        


def delete_messages(service):
    return service.users().messages().batchDelete(
        userId='me',
        body={
            'ids':read_mail(service,messages)
}
        
    ).execute()

delete_messages(service)