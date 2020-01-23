import random
import string

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

def random_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
