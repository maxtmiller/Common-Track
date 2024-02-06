import datetime
import os
import json

from cs50 import SQL
from flask import redirect, session, request, current_app
from functools import wraps

import os.path
from sqlite3 import Error
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta


# From CS50 Course
def login_required(f):
    """Decorate routes to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:

            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def before_first_request(f):
    """Decorate routes to execute before first request"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_app.config.get("BEFORE_FIRST_REQUEST"):

            return f(*args, **kwargs)

            current_app.config["BEFORE_FIRST_REQUEST"] = True

    return decorated_function


def run_sql(sql_file):
    """Runs SQL Commands from SQL File"""

    db = SQL("sqlite:///storage.db")

    try:
        with open('./static/'+sql_file, 'r', encoding="cp437") as file:
            sql_commands = file.read().split(';')
        for command in sql_commands:
            if command.strip():
                db.execute(command)
    except Error as e:
        print(e)


def check_for_sql(app):
    """Runs SQL files if they have not been run before"""

    db = SQL("sqlite:///storage.db")

    if not app.config.get("BEFORE_CHECK_EXECUTED"):

        run_sql('framework.sql')

        commonapp_list_len = db.execute("SELECT COUNT(Common_App_Member) FROM CollegeList;")[0]['COUNT(Common_App_Member)']
        ranking_list_len = db.execute("SELECT COUNT(institution) FROM CollegeRanking;")[0]['COUNT(institution)']

        if commonapp_list_len == 0:
            run_sql('list.sql')

        if ranking_list_len == 0:
            run_sql('ranking.sql')

            return

        app.config["BEFORE_CHECK_EXECUTED"] = True


def clear_session(app):
    """Clears Session and redirects to login page"""

    if not app.config.get("BEFORE_REQUEST_EXECUTED"):

        if request.endpoint != 'static' and request.endpoint != 'login':

            session.clear()

            return redirect("/login")

        app.config["BEFORE_REQUEST_EXECUTED"] = True


def is_digit(deadline):
    """Checks if a string has a digit"""

    return any(char.isdigit() for char in deadline)


def authentication():
    """Authenticates Google API"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    if os.path.exists('token.json'):
        # with open('token.json', 'r') as file:
        #     data = json.load(file)
        # expiry_string = data.get('expiry', '')
        # expiry_datetime = datetime.fromisoformat(expiry_string[:-1])
        # print("expiry_datetime", expiry_datetime)
        # print("datetime.now()", datetime.now())
        # if expiry_datetime < datetime.now():
        #     print("true")
        #     os.remove('token.json')
        #     creds = None
        # else:
        #     creds = Credentials.from_authorized_user_file('token.json')
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./static/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    return service


def check_for_calendar(service):
    """Check for existing college deadline calendar"""

    try:
        calendars = service.calendarList().list().execute().get('items', [])

        for calendar in calendars:
            if calendar['summary'] == "College Deadlines":
                calendarId = calendar['id']
                return calendarId
        return False

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_calendar(service):
    """Creates new calendar for storing college deadline events"""

    try:
        calendar = {
            'summary': 'College Deadlines',
            'timeZone': 'Europe/Vienna'
        }

        created_calendar = service.calendars().insert(body=calendar).execute()
        calendarId = created_calendar['id']

        return calendarId

    except HttpError as error:
        print(f"An error occurred: {error}")


def check_for_events(college_name, deadline, date, calendarId):
    """Check for existing college deadlines events"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/workspaces/67687590/final/static/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds, developerKey="AIzaSyBbHKdaFdOah6lbsdjzbf4Bp2ZJQRihEwc")

        college_name = college_name
        deadline = deadline
        date = date

        start_time = (datetime.fromisoformat(date) - timedelta(days=1)).isoformat()+"Z"
        end_time = (datetime.fromisoformat(date) + timedelta(days=1)).isoformat()+"Z"

        events = service.events().list(
            calendarId=calendarId,
            timeMin=start_time,
            timeMax=end_time,
            q=college_name
        ).execute()

        print("events", events)

        if events.get('items'):
            print(f"Events found with name '{college_name}':")
            print("ARRAY? - ", [event['id'] for event in events['items']])
            for event in events['items']:
                print(f"  - {event['summary']} ({event['start']['dateTime']})")
                return event['id']
        else:
            print(f"No events found with name '{college_name}'.")
            return False

    except HttpError as error:
        print(f"An error occurred: {error}")


def events_in_calendar(calendarId):
    """List out all existing university deadlines"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/workspaces/67687590/final/static/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds, developerKey="AIzaSyBbHKdaFdOah6lbsdjzbf4Bp2ZJQRihEwc")

        events = service.events().list(
            calendarId=calendarId,
        ).execute()

        print("events", events)
        college = []

        if events.get('items'):
            print("All events in Calendar after Now")
            for event in events['items']:
                print(f"  - {event['summary']} ({event['start']['dateTime']})")
                college.append({'name': event['summary'], 'deadline': event['description'] })
            return college
        else:
            print("No events found")
            return False

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_event(service, college_name, deadline, date, isDuplicate, isSubmitted, calendarId):
    """Create new college deadline event"""

    try:
        college_name = college_name
        deadline = deadline
        date = date

        if not isDuplicate:
            event = {
                "summary": college_name,
                "location": "Online",
                "description": deadline + " Deadline",
                "colorId": 6,
                "start": {
                    "dateTime": date,
                    "timeZone": "Etc/UTC"
                },
                "end": {
                    "dateTime": date,
                    "timeZone": "Etc/UTC"
                },
                "attendees": [{
                    "email": "mtmlr101@gmail.com",
                    "responseStatus": "accepted"
                }]
            }

            event = service.events().insert(calendarId=calendarId, body=event).execute()

            print(f"Event created {event.get('htmlLink')}")
            isSubmitted = True

        else:
            print("Duplicate Event")
            isSubmitted = False

    except HttpError as error:
        print(f"An error occurred: {error}")


def delete_event(service, college_name, deadline, date, isDuplicate, isSubmitted, calendarId):
    """Deletes existing college deadline event"""

    try:
        college_name = college_name
        deadline = deadline
        date = date

        if isDuplicate:
            event = {
                "summary": college_name,
                "location": "Online",
                "description": deadline + " Deadline",
                "colorId": 6,
                "start": {
                    "dateTime": date,
                    "timeZone": "Etc/UTC"
                },
                "end": {
                    "dateTime": date,
                    "timeZone": "Etc/UTC"
                },
                "attendees": [{
                    "email": "mtmlr101@gmail.com",
                    "responseStatus": "accepted"
                }]
            }

            event = service.events().delete(calendarId=calendarId, eventId=isDuplicate).execute()

            print("Event Deleted")
            isSubmitted = True

        else:
            print("No Event")
            isSubmitted = False

    except HttpError as error:
        print(f"An error occurred: {error}")

