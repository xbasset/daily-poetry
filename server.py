# main server file
# Author: Xavier Basset
# Date: 2023/07/21
# Version: 1.0

# run every minute to check in the data to see if there is a poem to trigger

from email.message import EmailMessage
import os
import smtplib
import schedule
import time
from pyairtable import Table
from typing import List


from src.daily_poem import DailyPoem

FROM_EMAIL = "dailypoetry@hoomano.com"

# daily_poems_craft_list is a list of DailyPoem objects
daily_poems_craft_list: List[DailyPoem] = []


def craft_email(subject, from_email, to_email, content):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(content)

    return msg

def send_email(subject, from_email, to_email, content):
    msg = craft_email(subject, from_email, to_email, content)
    print("Sending email: " + msg['Subject'] + " to " + msg['To'])
    print(msg.get_content())
    # send the email
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #     smtp.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
    #     smtp.send_message(msg)


        


def load_data_from_airtable():
    _local_daily_poems_craft_list =[]
    # connect to airtable
    access_token = os.getenv('AIRTABLE_TOKEN_DAILYPOETRY')
    base_id = os.getenv('AIRTABLE_BASE_ID_DAILYPOETRY')
    table_name = os.getenv('AIRTABLE_DAILYPOETRY_USER_TABLENAME')  # Use table name here

    table = Table(access_token, base_id, table_name)

    # Get all Records 
    records = table.all()
    for record in records:
        # get the email
        email = record['fields']['email']
        # extract the time_of_day to send the email from format 2023-07-24T17:00:00.000Z
        time_of_day = record['fields']['time_of_day'].split("T")[1].split(".")[0]
        # get the customization infos
        personalization = record['fields']['personalization']
        # get the style
        style = record['fields']['style']

        _local_daily_poems_craft_list.append(DailyPoem(email, time_of_day, personalization, style))
    return _local_daily_poems_craft_list


daily_poems_craft_list = load_data_from_airtable()


for poem in daily_poems_craft_list:
    print(poem)
    print(poem.content)
    schedule.every().day.at(poem.time_of_day).do(send_email, "Daily Poem", FROM_EMAIL, poem.email, poem.content)




while True:
   schedule.run_pending()
   time.sleep(1)
   print("Looking at poems to send")
