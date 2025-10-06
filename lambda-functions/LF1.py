import json

def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    resp = None

    if intent_name == 'GreetingIntent':
        return 
    elif intent_name == 'DiningSuggestionsIntent':
        return
    else: 
        return 

def lambda_handler(event, context):
    resp = dispatch(event)
    return resp