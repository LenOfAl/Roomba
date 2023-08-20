# pylint: skip-file

import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor

import pyfiglet
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


with open('keywords.txt',encoding="utf-8") as f:
    KEY_WORDS= [line[:-1] for line in f]

class Gmail:
    """
    Gmail class to authenticate and delete spam emails
    """
    def  __init__(self):
        print('*'*60)
        print('*'*60)
        print(pyfiglet.figlet_format("ROOMBA", font="slant"))
        print('*'*60)
        print('*'*60)
        print("\n"*2)

        if not 'Roomba' in os.getcwd():
            os.chdir(os.getcwd()+'/Roomba')
        
        self.service=self.gmail_authenticate()
        start_time = time.time()
        mail_ids=self.search_mails("")

        """
            make mail ids chucnk of 40 and call read_mail function with multithreading
        """
        mail_ids_chunks=list(self.mails_to_chunks(mail_ids,40))
        spam_mail_ids=[]
        with ProcessPoolExecutor (max_workers=4) as executor:
            t= executor.map(self.read_mail,mail_ids_chunks)
            for spams in t:
                spam_mail_ids.extend(spams)
        self.delete_messages(spam_mail_ids)

        print('------------------')
        print(f'Scanned {len(mail_ids)} emais')
        print(f'Deleted {len(spam_mail_ids)} of {len(mail_ids)}')
        print(f"Total time taken {time.time()-start_time} seconds")
        print('------------------')


    def gmail_authenticate(self):
        """
        Authenticate to gmail using OAuth2
        """
        scopes = ['https://mail.google.com/']

        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid :
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port = 0)
            
            with open("token.pickle", "wb") as token:
                pickle.dump(creds,token)
        return build('gmail', 'v1', credentials=creds)


    def search_mails(self,query):
        """
        Search for mails in inbox
        """
        result=self.service.users().messages().list(userId='me').execute()
        messages=[]
        if 'messages' in result:
            messages.extend(result['messages'])
        while 'nextPageToken' in result:
            page_token=result['nextPageToken']
            result = self.service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
            if 'messages' in result:
                messages.extend(result['messages'])
        print(f"Found {len(messages)} emails")
        return messages
    
    def read_mail(self,messages_ids):
        """
        Read the mail and check if it is spam
        """
        ids=[]
        message_count=0
        for message in messages_ids:
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
    
    def delete_messages(self,spam_mail_ids):
        """
        Delete the spam mails
        """
        mail_chunks=list(self.mails_to_chunks(spam_mail_ids))
        for mails in mail_chunks:
            self.service.users().messages().batchDelete(userId='me',body={'ids':mails}).execute()
    
    def mails_to_chunks(self,mails,n=1000):
        """
        Split the mails into chunks of 1000
        """
        for i in range(0, len(mails), n): 
            yield mails[i:i + n]


class Email:
    """
    Email class to store email data
    """
    def __init__(self,email_data,from_addr,email_id) -> None:
        self.subject= [j['value'] for j in email_data if j["name"]=="Subject"]
        self.from_addr=from_addr
        self.id=email_id
    
    def is_spam(self):
        """
        Check if the email is spam
        """
        for sub in self.subject:
            sub=sub.lower()
            for keyword in KEY_WORDS:
                if keyword in sub:
                    print(*self.subject,self.from_addr)
                    return True




if __name__=="__main__":
    gmail=Gmail()




