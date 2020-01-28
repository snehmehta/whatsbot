import datetime
import pickle
import datefinder
import os.path
import json
import helper
import gspread
import datetime
import string

from sheets import Gspread
from flask import Flask,request,jsonify,make_response,Response
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)

scope = ["https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "Whatsbot-58a18b101200.json", scopes=scope)

client = gspread.authorize(creds)
all_sheet = client.open("Whatsbot appointment")
sheet = all_sheet.worksheet("Sheet1")


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

#Avaliable time slots
@app.route('/timeslots',methods=['POST','GET'])
def timeslots():
    msg = request.form.get('Memory')
    temp = json.loads(msg)
    barber = temp['twilio']['collected_data']['schedule_appt']['answers']['booking_selection_1']['answer']
    date = temp['twilio']['collected_data']['schedule_appt']['answers']['booking_selection_2']['answer']

    gsp = Gspread(sheet)
    available_slot = gsp.get_slots(date,barber)
    available_slot = [("Enter " + str(i[0] + 1) +"  "+ i[1] + "\n") for i in enumerate(available_slot)]
    slots = "".join(available_slot)
    return make_response(jsonify(helper.create_say_redirect_response(slots,"task://booking_part_1")),200)

# Call the Calendar API
@app.route('/eventList',methods=['POST','GET'])
def get_event():
    timzone = datetime.datetime.utcnow()

    now = datetime.datetime(timzone.year,timzone.month,timzone.day,timzone.hour,timzone.minute,timzone.second).isoformat() + 'Z'  # 'Z' indicates UTC time
    end = datetime.datetime(timzone.year,timzone.month,timzone.day,20,00,00).isoformat() + 'Z'

    event_list = []
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          timeMax=end, singleEvents=True,
                                          orderBy='startTime',timeZone=str(timzone.tzname)).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(event['summary'])

    return make_response(jsonify(helper.create_say_response(event_list)),200)
 
@app.route('/eventCreate',methods=['Post'])
def create_event():

    msg = request.form.get('Memory')
    temp = json.loads(msg)

    date =  temp['twilio']['collected_data']['schedule_appt']['answers']['booking_selection_2']['answer']
    part_number = temp['twilio']['collected_data']['collect_timeslot']['answers']['selected_timeSlot']['answer']
    barber = temp['twilio']['collected_data']['schedule_appt']['answers']['booking_selection_1']['answer']

    token = helper.random_token()

    gsp = Gspread(sheet)

    available_slot = gsp.get_slots(date,barber)
    part_selected = available_slot[int(part_number)-1]

    duration=20
    description=None
    location=None

    start_time = gsp.add_appointment(part_selected,token,barber,date)
    end_time = start_time + timedelta(minutes=duration)

    summary = barber + " " + str(token) 

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
        message = "Your token is : " + token + "\nYour time is :" + str(start_time.time()) + "\n Date is : " + date
        return make_response(jsonify(helper.create_say_response(message)),200)
    else:
        return make_response(jsonify(helper.create_say_response("Sorry failed")),200)


if __name__ == "__main__":
    app.run(debug=True)
