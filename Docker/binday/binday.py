import urllib.request

import csv

from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def check_row(row):
    if row[0] != 839342:
        return False
    return True

def get_data(filename, check=True):
    with open(filename, "rb") as csvfile:
        datareader = csv.reader(csvfile)
        yield next(datareader)  # yield the header row
        for row in datareader:
            if check == False: # Bypass check
                yield row
            else:
                if check_row(row):
                    yield row

def google_auth():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('data/token.json'):
        creds = Credentials.from_authorized_user_file('data/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('data/token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def create_event(service, dateString, bin):
        binDate = datetime.strptime(dateString, '%d/%m/%Y')
        binDateTime = binDate.isoformat()

        event_result = service.events().insert(calendarId='primary',
            body={
                "summary": bin,
                "start": {"dateTime": binDateTime, "timeZone": 'Europe/London'},
                "end": {"dateTime": binDateTime, "timeZone": 'Europe/London'},
                'reminders': {'useDefault': False},
            }
        ).execute()

        print("Event created")
        print("id: ", event_result['id']) # Add to bin list
        print("bin colour: ", event_result['summary'])
        print("Date: ", event_result['start']['dateTime'])
        return event_result['id']



def main():
    # Setup google tokens.
    service = google_auth()

    # Download latest version of bin day csv
    urllib.request.urlretrieve("http://opendata.leeds.gov.uk/downloads/bins/dm_jobs.csv", "/data/raw.csv")

    # Retrieve and filter bin data from downloaded file
    downloadedBinDays = []
    for row in get_data("/data/raw.csv"):
        # process row
        downloadedBinDays.append((row[2], row[1]))

    
    # Compare to previously saved data (if exists)
    if os.path.exists('/data/bin_events.csv'):
    #     # Open and compare
    #     with open('/data/bin_events.csv', 'r') as fp:
    #         s = fp.read()

        # Bin days from fil with past dates deleted. They will still be in historic file.
        existingBinDays = []
        for binDay in get_data('/data/bin_events.csv', check=False):
            if datetime.strptime(binDay(0), '%d/%m/%Y') < datetime.now():
                existingBinDays.append(binDay)

        # New bin days that are not already in file
        newBinDays = []
        for binDay in downloadedBinDays:
            if binDay(0) not in existingBinDays: # Check if date is in file
                newBinDays.append(binDay)

        sortedBinDays = newBinDays.sort(key=lambda tup: datetime.strptime(tup[0], '%d/%m/%Y'))
    else:
        # all data is new.
        sortedBinDays = downloadedBinDays.sort(key=lambda tup: datetime.strptime(tup[0], '%d/%m/%Y'))

    # Create calendar event for each new bin day
    createdBinDays=[]
    for binDay in sortedBinDays: 
        id = create_event(service, binDay(0), binDay(1))
        createdBinDays.append((binDay(0), binDay(1), id))

    
    # Existing bin days (from file) with new, unique days added in.
    totalBinDays = existingBinDays + createdBinDays
    # Overwrite current file with new dates bin_events.csv
    with open('/data/bin_events.csv', mode='w') as binEventFile:
        binEventWriter = csv.writer(binEventFile, delimiter=',', fieldnames = ['Date','Bin','Event_ID'])
        for row in totalBinDays:
            binEventWriter.writerow(row)

    #Add events to historic file or create new file if doesnt exist 
    with open('/data/historic_bin_events.csv', mode='a') as binHistoricFile:
        binHistoricWriter = csv.writer(binHistoricFile, delimiter=',', fieldnames = ['Date','Bin','Event_ID'])
        for row in createdBinDays:
            binHistoricWriter.writerow(row)
            

if __name__ == '__main__':
    main()