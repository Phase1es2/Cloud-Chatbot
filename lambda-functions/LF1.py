import json
import boto3
import re
from datetime import datetime
from dateutil import parser

cuisine_type = ['Thai', 'Chinese', 'French', 'Japanese', 'Korean', 'Indian', 'American', 'Mexican']

def valid_date(date_str, time_str):
    d = datetime.strptime(date_str, '%Y-%m-%d').date()
    t = datetime.strptime(time_str, '%H:%M').time()
    reservation_dt = datetime.combine(d, t)
    now = datetime.now()
    if now > reservation_dt:
        return False
    return True

def normalize_date_time(date_str, time_str):
    try:
        d = parser.parse(date_str).date()
        t = parser.parse(time_str).time()
        return d.isoformat(), t.strftime("%H:%M")  # YYYY-MM-DD, HH:MM
    except Exception:
        return None, None

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def elicit_slot(intent, slots, slot_to_elicit, message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit
            },
            "intent": {
                "name": intent,
                "slots": slots
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }

def delegate(intent, slots):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
            },
            "intent": {
                "name": intent,
                "slots": slots
            }
        }
    }

def close(intent, slots, message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent,
                "slots": slots,
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }


def valid_booking(location, date_str, time_str, num_people, cuisine, email):
    if location != 'Manhattan':
        return {
            'isValid': False,
            'violatedSlot': 'Location',
            'message': f"Sorry, we do not have service in {location}, we only provide service in Manhattan now, wher do you want to eat?"
        }

    if not valid_date(date_str, time_str):
        return {
            'isValid': False,
            'violatedSlot': 'DATE',
            'message': 'The date and time of the reservation should be at least 24 hours in advance.'
        }

    if cuisine not in cuisine_type:
        return {
            'isValid': False,
            'violatedSlot': 'CUISINE',
            'message': f"We do not have {cuisine}, would you like a different type of cuisine?"
        }

    if int(num_people) > 20:
        return {
            'isValid': False,
            'violatedSlot': 'NumOfPeople',
            'message': 'The maximum number of people for a reservation is 20.'
        }

    if not is_valid_email(email):   # <-- FIXED here
        return {
            'isValid': False,
            'violatedSlot': 'EMAIL',
            'message': 'The email address is invalid.'
        }

    return {'isValid': True}

def safe_get(slot, key="interpretedValue"):
    if slot and "value" in slot and key in slot["value"]:
        return slot["value"][key]
    return None

def dining_suggestions(intent, slots, event):
    # safely pull slot values
    location = safe_get(slots.get('Location'))
    date_str = safe_get(slots.get('DATE'))
    time_str = safe_get(slots.get('DiningTime'))
    num_people = safe_get(slots.get('NumOfPeople'))
    cuisine = safe_get(slots.get('CUISINE'))
    email = safe_get(slots.get('EMAIL'))

    # normalize natural date/time input if provided
    if date_str or time_str:
        date_str, time_str = normalize_date_time(date_str, time_str)

    if event['invocationSource'] == 'DialogCodeHook':
        # run validation only if all slots are filled
        if location and date_str and time_str and num_people and cuisine and email:
            booking_result = valid_booking(location, date_str, time_str, num_people, cuisine, email)

            if not booking_result['isValid']:
                slots[booking_result['violatedSlot']] = None
                return elicit_slot(
                    intent,
                    slots,
                    booking_result['violatedSlot'],
                    booking_result['message']
                )


        return delegate(intent, slots)

    if event['invocationSource'] == 'FulfillmentCodeHook':
        return close(
            intent,
            slots,
            "You're all set. Expect my suggestions shortly! Have a good day."
        )

def greeting():
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": "GreetingIntent",
                "state": "Fulfilled"
            }
        },
        "messages": [ 
            {
                "contentType": "PlainText",
                "content": "Hi there, how can I help?"
            }
        ]
    }
    

def thank_you():
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": "ThankYouIntent",
                "state": "Fulfilled"
            }
        },
        "messages": [ 
            {
                "contentType": "PlainText",
                "content": "Thank you for using our service. The email will arrive shortly."
            }
        ]
    }

def handle_intent(intent, slots, event):
    if intent == 'GreetingIntent':
        return greeting()
    elif intent == 'DiningSuggestionsIntent':
        return dining_suggestions(intent, slots, event)
    elif intent == 'ThankYouIntent':
        return thank_you()

def lambda_handler(event, context):
    print(event)
    bot = event['bot']['name']
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    print(bot)
    print(slots)
    print(intent)
    return handle_intent(intent, slots, event)