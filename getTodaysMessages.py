from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
PeerChannel
)
import pandas as pd


import csv


class Scraper():
    def __init__(self):
        #Enter Your 7 Digit Telegram API ID.
        self.api_id =  28047309 
        #Enter Yor 32 Character API Hash
        self.api_hash = 'd835c210058ea452f8406e5a80ae2756'
        #Enter Your Mobile Number With Country Code.
        self.phone = '+447912177831'   

        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        self.groups=[]

    def connect(self):
        #connecting to telegram and checking if you are already authorized. 
        #Otherwise send an OTP code request and ask user to enter the code 
        #they received on their telegram account.
        #After logging in, a .session file will be created. This is a database file which makes your session persistent.
        
        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            self.client.sign_in(self.phone, input('Enter verification code: '))
           
    def getGroups(self):
        #with this method you will get all your group names
        #offset_date and  offset_peer are used for filtering the chats. We are sending empty values to these parameters so API returns all chats
        #offset_id and limit are used for pagination.
        #limit is 200. it means last 200 chats of the user.
        
        chats = []
        last_date = None
        chunk_size = 200
        result = self.client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash = 0
                ))
        chats.extend(result.chats)
        
        
        for chat in chats:
            try:
                if chat.megagroup== True:
                    self.groups.append(chat)
            except:
                continue

        #choose which group you want to scrape  members:
        for i,g in enumerate(self.groups):
            print(str(i) + '- ' + g.title)
            
     
    def checkDate(self, date):
            from datetime import datetime
            today = str(datetime.today().strftime('%Y-%m-%d'))

            
            if today == date:
                return(True)
            else:
                return(False)
    
    def getUsers(self):
        # with this method you will get group all members to csv file that you choosed group.
        
        g_index = input("Please! Enter a Number: ")
        target_group=self.groups[int(g_index)]


        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0
        total_count_limit = 0

        while True:
            print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
            history = self.client(GetHistoryRequest(
                peer=target_group,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_id = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break

        
        todaysActiveUsers = []

        
        with open(target_group.title+"Messages.csv","w",encoding='UTF-8') as f:#Enter your file name.
            
            for message in all_messages:
                messageDate = str(message.get("date")).split(" ")[0]
                

                if self.checkDate(messageDate):
                    
                    userId = message.get("from_id").get("user_id")
                    print( userId )

                    todaysActiveUsers.append(str(userId))

        return(todaysActiveUsers)


    def getTelegramTags(self,users):

        print("comparing user Ids with telegram tags ........")
        data = pd.read_csv("FrontdoorMembers.csv",  engine='python')
        data_dict = data.to_dict(orient="records")
        

        activeUserTags = [ ]
        
        for user in data_dict:
            id = user.get("user id")
            tag = user.get("username")
            
            if str(id) in users:
                activeUserTags.append(tag)

        return(activeUserTags)

        

    def searchAirtable(self,userTags):
        import requests

        # Replace with your Airtable API key
        api_key = 'keyKxJeKUVJjLloFI'

        # Replace with the base ID of your Airtable
        base_id = 'appq7vvHCwEfCmmYb'

        # Replace with the name of the table you want to search in
        table_name = 'Activity%20Tracker'

        # Replace with the name of the field you want to search in
        field_name = 'telegramHandle'

        # Replace with the value you want to search for
        search_value = '@ashprabaker'

        # Construct the URL for the search
        url = f'https://api.airtable.com/v0/{base_id}/{table_name}?filterByFormula=({field_name}="{search_value}")'

        # Execute the search
        response = requests.get(url, headers={'Authorization': 'Bearer ' + api_key})

        # Parse the JSON response
        responseData = response.json()

        print(responseData)

        # Get the first record that matches the search
        record = responseData['records'][0]

        # Get the ID of the record
        record_id = record['id']

        # Replace with the name of the field you want to input the value in
        input_field_name = 'activity'

        # Replace with the value you want to input
        input_value = '0'

        # Construct the URL for inputting the value
        url = f'https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}'
        print(url)
        # Execute the update
        response = requests.patch(url, json={input_field_name: input_value}, headers={'Authorization': 'Bearer ' + api_key})

        # Print the status code of the response
        print(response)
        print(requests.get(url, headers={'Authorization': 'Bearer ' + api_key}).json())




    
if __name__ == '__main__':
    telegram = Scraper()
    telegram.connect()
    telegram.getGroups()
    users = telegram.getUsers()
    userTags = telegram.getTelegramTags(users)
    print(userTags)
    telegram.searchAirtable(userTags)
