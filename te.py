import datetime
import pickle
import datefinder
import os.path
import random 
import string
import json

from flask import Flask,request
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from twilio.twiml.messaging_response import MessagingResponse

# from IPython.core.debugger import set_trace

app = Flask(__name__)


SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)


# Root Page
@app.route('/')
def index():
    return '<H1>Calendar</H1'

# Call the Calendar API
@app.route('/eventList')
def get_event():
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    event_list = []
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(event['summary'])

    return str(event_list)


@app.route('/eventCreate',methods=['Post'])
def create_event():
    msg = request.form.get('Memory')
    temp = json.loads(msg)
    time = temp['twilio']['collected_data']['schedule_appt']['answers']['appt_time']['answer']
    date =  temp['twilio']['collected_data']['schedule_appt']['answers']['appt_date']['answer']
    phone_number =  temp['twilio']['collected_data']['schedule_appt']['answers']['appt_phone_number']['answer']
    
    start_time_str = date + " " + time
    token = random_token()
    summary = "Appointment " + str(phone_number) + str(token)
    
    duration=30
    description=None
    location=None

    # matches = list(datefinder.find_dates(start_time_str))
    # if len(matches):
    start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
    end_time = start_time + timedelta(minutes=duration)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    iscompleted = service.events().insert(calendarId='primary', body=event).execute()
    if iscompleted:
        return "Completed"
    else:
        return "Failed"  

def random_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

if __name__ == "__main__":
    app.run(debug=True)
