from __future__ import print_function
from datetime import datetime
import pickle
import os.path
import logging
import pytz
import json

#import googleAuth
from . import googleAuth

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse
from oauth2client.client import AccessTokenCredentials

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SCOPES = ['https://www.googleapis.com/auth/calendar']
FORMAT = '%Y-%m-%d %H:%M'
# The latest time we want for events
END_OF_DAY = datetime.now(pytz.timezone("Australia/Melbourne")).replace(hour=23, minute=59).isoformat()
logger.info(END_OF_DAY)

# this user agent is chosen arbitrarily, might change if a better option is available
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Silk/44.1.54 like Chrome/44.0.2403.63 Safari/537.36"

def credentials(bucket, tokenFile):
    token = googleAuth.accessToken(bucket, tokenFile)
    creds = AccessTokenCredentials(token, USER_AGENT)
    return creds

# This commented code uses the old way of credentials.json and token.pickle to get credentials
# def credentials():
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)  
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             filename = os.path.join(os.path.dirname(__file__), 'credentials.json')
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 filename, SCOPES)
#             creds = flow.run_local_server()
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#         return None
#     else:
#         return creds

def getEventsFromJSON(eventsJSON):
    events = []
    for event in eventsJSON["events"]:
        events.append((event['name'], event['start'], event['end']))
    return events

def getEvents(bucket, tokenFile):
    """
    :rtype: List of 3-tuple: (str, str, str): (eventName, startdatetime, enddatetime)

    if credentials are valid, obtain the events from current time to 
    just before midnight of that day and return events as a list of events
    """
    creds = credentials(bucket, tokenFile)
    if credentials == None:
        raise Exception("credentials not available")

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    current = datetime.now(pytz.timezone("Australia/Melbourne")).isoformat()
    logger.info(current)
    events_result = service.events().list(calendarId='primary', timeMin=current, timeMax=END_OF_DAY,
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
    logger.info(result)
    return result

# TODO: createEvent is working, but summary not showing up
# def createEvent(name, startDateTime, endDateTime, creds=None):
#     if creds == None:
#         raise Exception("credentials not available")

#     service = build('calendar', 'v3', credentials=creds)
#     event = {
#       'summary': name,
#       'start': {
#         'dateTime': datetimeToIso(startDateTime, UTC_DIFF),
#         'timeZone': 'Australia/Melbourne',
#       },
#       'end': {
#         'dateTime': datetimeToIso(endDateTime, UTC_DIFF),
#         'timeZone': 'Australia/Melbourne',
#       },
#     }
#     event = service.events().insert(calendarId='primary', body=event).execute()

if __name__ == '__main__':
    print(getEvents())
