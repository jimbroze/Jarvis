from __future__ import print_function
from datetime import datetime, timedelta
import os

# from types import new_class
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

import urllib.request

import csv

locationCode = os.environ.get("LOCATION_CODE")
calId = os.environ.get("CAL_ID")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def check_row(row):
    if row[0] != locationCode:
        return False
    return True


def get_data(filename, check=True):
    with open(filename, "rt") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            if check == False:  # Bypass check
                yield row
            else:
                if check_row(row):
                    yield row


def get_service():
    """Get a service that communicates to a Google API."""

    print("Authenticating with google")
    credentials = service_account.Credentials.from_service_account_file(
        "/data/service.json"
    )
    # Build the service object.
    service = build("calendar", "v3", credentials=credentials)

    print("Authentication complete")
    return service


def create_event(service, dateString, bin):
    binDate = datetime.strptime(dateString, "%d/%m/%y").strftime("%Y-%m-%d")

    event_result = (
        service.events()
        .insert(
            calendarId=calId,
            body={
                "summary": bin,
                "start": {"date": binDate, "timeZone": "Europe/London"},
                "end": {"date": binDate, "timeZone": "Europe/London"},
                "reminders": {"useDefault": False},
            },
        )
        .execute()
    )

    return event_result["id"]


def main():
    # Setup google tokens.
    service = get_service()

    # Download latest version of bin day csv
    print("Downloading bin data")
    urllib.request.urlretrieve(
        "http://opendata.leeds.gov.uk/downloads/bins/dm_jobs.csv", "/data/raw.csv"
    )
    print("Download complete")

    # Retrieve and filter bin data from downloaded file
    print("Filtering downloaded data")
    # downloadedBinDays = []
    # for row in get_data("/data/raw.csv"):
    #     # process row
    #     downloadedBinDays.append((row[2], row[1]))
    downloadedBinDays = [(binDay[2], binDay[1]) for binDay in get_data("/data/raw.csv")]
    print("Filtering complete")

    # Bin days from file with past dates deleted.
    # Compare to previously saved data (if exists)
    if os.path.exists("/data/bin_events.csv"):
        print("bin events file found. Comparing file with new events.")

        # Only include future dates. Past dates will still be in historic file.
        # for binDay in get_data("/data/bin_events.csv", check=False):
        #     if datetime.strptime(
        #         binDay[0], "%d/%m/%y"
        #     ) > datetime.now() - datetime.timedelta(days=1):
        #         existingBinDays.append(binDay)
        existingBinDays = [
            binDay
            for binDay in get_data("/data/bin_events.csv", check=False)
            if datetime.strptime(binDay[0], "%d/%m/%y")
            > datetime.now() - timedelta(days=1)
        ]

        # New bin days that are not already in file
        daysToCompare = [
            (i[0], i[1]) for i in existingBinDays
        ]  # Lose IDs for comparison
        newBinDays = [
            binDay for binDay in downloadedBinDays if binDay not in daysToCompare
        ]

        print("Compare complete")
    else:
        print("No bin events file found. A new one will be created")
        # all data is new.
        newBinDays = downloadedBinDays
        existingBinDays = []

    newBinDays = list(set([i for i in newBinDays]))
    # Use above to get rid of all?

    newBinDays.sort(key=lambda tup: datetime.strptime(tup[0], "%d/%m/%y"))

    # Create calendar event for each new bin day
    createdBinDays = []
    eventCount = 0
    print("Creating events")
    for binDay in newBinDays:
        id = create_event(service, binDay[0], binDay[1].capitalize() + " bin")
        createdBinDays.append((binDay[0], binDay[1], id))
        eventCount += 1

    print(str(eventCount) + " events created.")

    # Existing bin days (from file) with new, unique days added in.
    totalBinDays = existingBinDays + createdBinDays
    # Overwrite current file with new dates bin_events.csv
    with open("/data/bin_events.csv", mode="w") as binEventFile:
        binEventWriter = csv.writer(binEventFile, delimiter=",")
        for row in totalBinDays:
            binEventWriter.writerow(row)

    # Add events to historic file or create new file if doesnt exist
    with open("/data/historic_bin_events.csv", mode="a") as binHistoricFile:
        binHistoricWriter = csv.writer(binHistoricFile, delimiter=",")
        for row in createdBinDays:
            binHistoricWriter.writerow(row)


if __name__ == "__main__":
    main()
