from __future__ import print_function
from datetime import datetime
import pickle
import os.path
from . import sort
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
FORMAT = '%Y-%m-%d %H:%M'
UTC_DIFF = '+11:00'
# The latest time we want for events
MAX_TIME = datetime.now().strftime("%Y-%m-%d") + "T23:59:59.999999" + UTC_DIFF

def datetimeToIso(datetimeObject, utcDifference):
    return datetimeObject.isoformat() + utcDifference

def credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)  
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            filename = os.path.join(os.path.dirname(__file__), 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                filename, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        return None
    else:
        return creds


def getEvents():
    """
    :rtype: List of 3-tuple: (str, str, str): (eventName, startdatetime, enddatetime)

    if credentials are valid, obtain the events from current time to 
    just before midnight of that day and return events as a list of events
    """
    creds = credentials()
    if credentials == None:
        raise Exception("credentials not available")

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    current = datetimeToIso(datetime.now(), UTC_DIFF) # +'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=current, timeMax=MAX_TIME,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return None
    result = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        startStr = datetime.strftime(parse(start), FORMAT)
        endStr = datetime.strftime(parse(end), FORMAT)
        result.append((event['summary'], startStr, endStr))
    return result

# TODO: summary is not working
def createEvent(name, startDateTime, endDateTime, creds=None):
    if creds == None:
        raise Exception("credentials not available")

    service = build('calendar', 'v3', credentials=creds)
    event = {
      'summary': name,
      'start': {
        'dateTime': datetimeToIso(startDateTime, UTC_DIFF),
        'timeZone': 'Australia/Melbourne',
      },
      'end': {
        'dateTime': datetimeToIso(endDateTime, UTC_DIFF),
        'timeZone': 'Australia/Melbourne',
      },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()

if __name__ == '__main__':
    print(getEvents())
