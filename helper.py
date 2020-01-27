import random
import string
from dateutil import tz
import datetime


def cur_time():

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Kolkata')

    utc = datetime.datetime.utcnow()

    utc = utc.replace(tzinfo=from_zone)

    central = utc.astimezone(to_zone)
    return central


def create_say_response(say):
    response = {
        "actions": [
            {
                "say": say
            }
        ]
    }
    return response


def create_say_redirect_response(say, redirect):
    response = {
        "actions": [
            {
                "say": say
            },
            {
                "redirect": redirect
            }
        ]
    }
    return response


def create_collect_redirect_response(say, redirect):
    response = {
        "actions": [
            {
                "collect": {
                    "name": "collect_comments",
                    "questions": [
                        {
                            "question": say,
                            "name": "comments",
                            "type": "Twilio.NUMBER"
                        }
                    ],
                    "on_complete": {
                        "redirect": redirect
                    }
                }
            }
        ]
    }
    return response

def random_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
