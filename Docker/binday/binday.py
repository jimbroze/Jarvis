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
            if check == False:
                yield row
            else:
                if check_row(row):
                    yield row

def google_auth():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def create_event(service, date, bin):
    # creates one hour event tomorrow 10 AM IST
        d = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        tomorrow = datetime(d.year, d.month, d.day, 10)+datetime.timedelta(days=1)
        start = tomorrow.isoformat()
        end = (tomorrow + datetime.timedelta(hours=1)).isoformat()

        event_result = service.events().insert(calendarId='primary',
            body={
                "summary": 'Automating calendar',
                "description": 'This is a tutorial example of automating google calendar with python',
                "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
                "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
            }
        ).execute()

        print("created event")
        print("id: ", event_result['id']) # Add to bin list
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime'])
        print("ends at: ", event_result['end']['dateTime'])
        return event_result['id']



def main():
    # Setup google tokens.
    service = google_auth()

    # Download latest version of bin day csv
    urllib.request.urlretrieve("http://opendata.leeds.gov.uk/downloads/bins/dm_jobs.csv", "/data/raw.csv")

    # Retrieve and filter bin data from downloaded file
    binDays = []
    for row in get_data("/data/raw.csv"):
        # process row
        binDays.append((row[2], row[1]))




    # Compare to previously saved data (if exists)
    if os.path.exists('/data/bin_events.csv'):
        # Open and compare
        get_data('/data/bin_events.csv', check=False)

        # Compare dates only

        newBinDays = binDays.sort(key=lambda tup: datetime.strptime(tup[0], '%d/%m/%Y'))
    else:
        # all data is new.
        newBinDays = binDays.sort(key=lambda tup: datetime.strptime(tup[0], '%d/%m/%Y'))



    createdBinDays=[]

    for binDay in newBinDays: # Create calendar event for each new bin day
        id = create_event(service, binDay(0), binDay(1))
        createdBinDays.append((binDay(0), binDay(1), id))


    #Add to file or create new file if doesnt exist 
    with open('/data/bin_events.csv', mode='a') as binEventFile:
        binEventWriter = csv.writer(binEventFile, delimiter=',', fieldnames = ['Date','Bin','Event_ID'])
        for row in createdBinDays:
            binEventWriter.writerow(row)

if __name__ == '__main__':
    main()