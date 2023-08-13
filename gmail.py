import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

os.chdir(os.getcwd()+'/Roomba')

keywords = []
with open('keywords.txt') as f:
    keywords= [line[:-1] for line in f]

SCOPES = ['https://mail.google.com/']

class Gmail:
    def __init__(self):
        self.service=self.gmailAuthenticate()
        mailIds=self.search_mails("is:unread")
        spamMailIds=self.read_mail(mailIds)
        self.delete_messages(spamMailIds)
        print('------------------')
        print('Scanned {} emais'.format(len(mailIds)))
        print('Deleted {} of {}'.format(len(spamMailIds),len(mailIds)))
        print('------------------')

    def gmailAuthenticate(self):
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


    def search_mails(self,query):
        result=self.service.users().messages().list(userId='me').execute()
        messages=[]
        if 'messages' in result:
            messages.extend(result['messages'])
        while 'nextPageToken' in result:
            page_token=result['nextPageToken']
            result = self.service.users().messages().list(userId='me',q=query,labelIds=['INBOX'], pageToken=page_token).execute()
            if 'messages' in result:
                messages.extend(result['messages'])
        return messages
    
    def read_mail(self,messagesIds):
        ids=[]
        message_count=0
        for message in messagesIds: 
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            message_count= message_count + 1
            email_data= msg['payload']['headers']
            for values in email_data:
                name = values["name"]
                if name == "From":
                    email=Email(email_data,values["value"],msg['id'])
                    if email.is_spam():
                        ids.append(email.id)
        return ids
    
    def delete_messages(self,spamMailIds):
        return self.service.users().messages().batchDelete(
            userId='me',
            body={
                'ids':spamMailIds
        }
            
        ).execute()

class Email:
    def __init__(self,email_data,from_addr,id) -> None:
        self.subject= [j['value'] for j in email_data if j["name"]=="Subject"]
        self.from_addr=from_addr
        self.id=id
    
    def is_spam(self):
        for s in self.subject:
            s=s.lower()
            for keyword in keywords:
                if keyword in s:
                    print(*self.subject,self.from_addr)
                    return True




if __name__=="__main__":
    gmail=Gmail()




